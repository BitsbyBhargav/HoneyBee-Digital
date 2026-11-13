"""Run a separate MySQL instance; never changes an existing Windows service."""
import argparse
import os
from pathlib import Path
import secrets
import subprocess
import time
import pymysql
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['start', 'stop'], nargs='?', default='start')
    parser.add_argument('--bin', default=r'C:\Program Files\MySQL\MySQL Server 8.0\bin')
    args = parser.parse_args()
    LOCAL.mkdir(exist_ok=True)
    env_path = ROOT / '.env'
    if not env_path.exists():
        env_path.write_text('\n'.join([
            'MYSQL_HOST=127.0.0.1', 'MYSQL_PORT=3307', 'MYSQL_DATABASE=honeybee',
            'MYSQL_USER=honeybee_app', f'MYSQL_PASSWORD={secrets.token_hex(24)}',
            f'MYSQL_ROOT_PASSWORD={secrets.token_hex(24)}',
            f'IMPORT_API_KEY={secrets.token_hex(32)}',
            'CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]', '']), encoding='utf-8')
    config = dotenv_values(env_path)
    if config.get('MYSQL_HOST') != '127.0.0.1' or config.get('MYSQL_PORT') != '3307':
        raise SystemExit('This helper only manages 127.0.0.1:3307. Use Compose or your own MySQL for other settings.')
    # The helper creates identifiers only from this fixed project configuration.
    if config.get('MYSQL_DATABASE') != 'honeybee' or config.get('MYSQL_USER') != 'honeybee_app':
        raise SystemExit('Local helper requires database honeybee and user honeybee_app.')
    connect = dict(host='127.0.0.1', port=3307, user='root',
                   password=config['MYSQL_ROOT_PASSWORD'], connect_timeout=2)
    marker = LOCAL / 'mysql-owned.txt'
    data = LOCAL / 'mysql'
    if args.action == 'stop':
        if not marker.exists():
            raise SystemExit('No project-owned instance; refusing to stop anything.')
        with pymysql.connect(**connect) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT @@datadir')
                if Path(cursor.fetchone()[0]).resolve() != data.resolve():
                    raise SystemExit('Port 3307 is not the project instance; refusing to stop it.')
                cursor.execute('SHUTDOWN')
        print('Project MySQL stopped. Existing MySQL80 service was not changed.')
        return
    try:
        with pymysql.connect(**connect) as connection:
            if not marker.exists():
                raise SystemExit('Port 3307 is already occupied by an unmanaged instance.')
            with connection.cursor() as cursor:
                cursor.execute('SELECT @@datadir')
                actual = Path(cursor.fetchone()[0]).resolve()
                if actual != data.resolve():
                    raise SystemExit('Port 3307 does not use the project data directory.')
        print('Project MySQL already running on 127.0.0.1:3307.')
        return
    except pymysql.err.OperationalError as exc:
        if exc.args[0] != 2003:
            raise SystemExit('Port 3307 is occupied or credentials differ. No changes made.')
    executable = Path(args.bin) / 'mysqld.exe'
    if not executable.exists():
        raise SystemExit('mysqld.exe not found; supply --bin or use Docker Compose.')
    if not data.exists():
        data.mkdir()
        with (LOCAL / 'mysql-init.log').open('wb') as log:
            subprocess.run([str(executable), '--no-defaults', '--initialize-insecure',
                            f'--basedir={executable.parent.parent}', f'--datadir={data}'],
                           stdout=log, stderr=log, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        marker.write_text(str(data.resolve()), encoding='utf-8')
        # Applied by MySQL before accepting clients. Passwords never enter process arguments.
        quote = lambda value: "'" + value.replace('\\', '\\\\').replace("'", "''") + "'"
        bootstrap = LOCAL / 'bootstrap.sql'
        bootstrap.write_text(
            f"ALTER USER 'root'@'localhost' IDENTIFIED BY {quote(config['MYSQL_ROOT_PASSWORD'])};\n"
            "CREATE DATABASE IF NOT EXISTS honeybee CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
            f"CREATE USER IF NOT EXISTS 'honeybee_app'@'localhost' IDENTIFIED BY {quote(config['MYSQL_PASSWORD'])};\n"
            "GRANT SELECT, INSERT, UPDATE ON honeybee.* TO 'honeybee_app'@'localhost';\n", encoding='utf-8')
    bootstrap = LOCAL / 'bootstrap.sql'
    command = [str(executable), '--no-defaults', f'--basedir={executable.parent.parent}',
               f'--datadir={data}', '--port=3307', '--bind-address=127.0.0.1', '--mysqlx=OFF',
               '--character-set-server=utf8mb4', '--collation-server=utf8mb4_unicode_ci',
               '--default-time-zone=+00:00', f'--log-error={LOCAL / "mysql-error.log"}',
               f'--pid-file={LOCAL / "mysql.pid"}']
    if bootstrap.exists():
        command.append(f'--init-file={bootstrap.as_posix()}')
    with (LOCAL / 'mysql-console.log').open('ab') as log:
        process = subprocess.Popen(command, stdout=log, stderr=log,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
    for _ in range(60):
        if process.poll() is not None:
            raise SystemExit('MySQL failed to start; inspect .local/mysql-error.log.')
        try:
            with pymysql.connect(**connect):
                pass
            bootstrap.unlink(missing_ok=True)
            print('Project MySQL ready on 127.0.0.1:3307. Credentials are in ignored .env.')
            return
        except pymysql.err.OperationalError:
            time.sleep(1)
    raise SystemExit('MySQL readiness timed out; inspect .local/mysql-error.log.')


if __name__ == '__main__':
    main()
