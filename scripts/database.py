"""Explicit schema setup and real MySQL dump/restore helpers."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from dotenv import dotenv_values
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.config import settings
from backend.app.database import Base
from backend.app import models  # registers table metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['setup', 'export', 'restore'])
    parser.add_argument('--file', type=Path, default=ROOT / 'database' / 'honeybee_dump.sql')
    parser.add_argument('--bin', default=r'C:\Program Files\MySQL\MySQL Server 8.0\bin')
    parser.add_argument('--database', help='Restore target; must be a new or explicitly chosen database.')
    args = parser.parse_args()
    config = dotenv_values(ROOT / '.env')
    root_password = config.get('MYSQL_ROOT_PASSWORD')
    if not root_password:
        raise SystemExit('Set MYSQL_ROOT_PASSWORD in .env for administrative setup/export/restore.')
    if args.action == 'setup':
        admin_url = settings.database_url.set(username='root', password=root_password)
        admin = create_engine(admin_url)
        Base.metadata.create_all(admin)
        args.file.parent.mkdir(exist_ok=True)
        # The schema file is generated from the same live MySQL table as the dump.
        with admin.connect() as connection:
            ddl = connection.exec_driver_sql('SHOW CREATE TABLE listing_master').one()[1]
        (ROOT / 'database' / 'schema.sql').write_text(ddl + ';\n', encoding='utf-8')
        print('listing_master schema ready.')
        return
    env = {**os.environ, 'MYSQL_PWD': root_password}
    common = [f'--host={settings.mysql_host}', f'--port={settings.mysql_port}', '--user=root',
              '--default-character-set=utf8mb4']
    if args.action == 'export':
        args.file.parent.mkdir(exist_ok=True)
        with args.file.open('wb') as output:
            subprocess.run([str(Path(args.bin) / 'mysqldump.exe'), *common,
                '--single-transaction', '--no-tablespaces', '--set-gtid-purged=OFF',
                '--skip-add-drop-table', settings.mysql_database, 'listing_master'],
                stdout=output, env=env, check=True)
        print(f'Populated MySQL dump written to {args.file.name}.')
    else:
        target = args.database
        if not target or not target.replace('_', '').isalnum() or target == settings.mysql_database:
            raise SystemExit('Restore requires --database NEW_NAME, different from the app database.')
        admin = create_engine(settings.database_url.set(username='root', password=root_password, database=None))
        with admin.begin() as connection:
            # Deliberately fails if the target exists; no existing data is overwritten.
            connection.exec_driver_sql(f'CREATE DATABASE `{target}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        with args.file.open('rb') as source:
            subprocess.run([str(Path(args.bin) / 'mysql.exe'), *common, target],
                           stdin=source, env=env, check=True)
        print(f'Dump restored into {target}.')


if __name__ == '__main__':
    main()
