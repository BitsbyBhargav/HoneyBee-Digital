"""Restore into a newly generated MySQL database and compare every column."""
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys
from dotenv import dotenv_values
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.config import settings


def digest(engine):
    with engine.connect() as connection:
        rows = [dict(row) for row in connection.execute(text('SELECT * FROM listing_master ORDER BY id')).mappings()]
    return len(rows), hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def main():
    target = 'honeybee_restore_' + secrets.token_hex(6)
    password = dotenv_values(ROOT / '.env')['MYSQL_ROOT_PASSWORD']
    url = settings.database_url.set(username='root', password=password)
    source = create_engine(url)
    admin = create_engine(url.set(database=None))
    restored = None
    try:
        subprocess.run([sys.executable, str(ROOT / 'scripts' / 'database.py'),
                        'restore', '--database', target], check=True)
        restored = create_engine(url.set(database=target))
        original = digest(source)
        copy = digest(restored)
        assert original == copy, 'Restore differs from source database.'
        report = {'restored_count': copy[0], 'all_columns_sha256': copy[1],
                  'exact_match': True, 'temporary_database_removed': True}
        (ROOT / 'docs').mkdir(exist_ok=True)
        (ROOT / 'docs' / 'dump-verification.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    finally:
        if restored:
            restored.dispose()
        source.dispose()
        with admin.begin() as connection:
            connection.exec_driver_sql(f'DROP DATABASE IF EXISTS `{target}`')
        admin.dispose()


if __name__ == '__main__':
    main()
