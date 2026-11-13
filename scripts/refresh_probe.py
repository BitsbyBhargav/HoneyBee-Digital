"""Browser-test helper: briefly remove and restore one backed-up project listing."""
import json
from pathlib import Path
import sys
from dotenv import dotenv_values
from sqlalchemy import create_engine, delete, select
from sqlalchemy.dialects.mysql import insert

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.config import settings
from backend.app.models import Listing


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {'remove', 'restore'}:
        raise SystemExit('Usage: refresh_probe.py remove|restore (used by the browser test)')
    backup = ROOT / '.local' / 'refresh-probe.json'
    password = dotenv_values(ROOT / '.env')['MYSQL_ROOT_PASSWORD']
    engine = create_engine(settings.database_url.set(username='root', password=password))
    if sys.argv[1] == 'remove':
        if backup.exists():
            raise SystemExit('A previous probe needs restoration. Run this helper with restore first.')
        with engine.begin() as connection:
            row = connection.execute(select(Listing.__table__).order_by(Listing.id.desc()).limit(1)).mappings().one()
            backup.parent.mkdir(exist_ok=True)
            backup.write_text(json.dumps(dict(row), default=str, ensure_ascii=False), encoding='utf-8')
            connection.execute(delete(Listing).where(Listing.id == row['id'], Listing.fingerprint == row['fingerprint']))
        print('One backed-up listing temporarily removed.')
    else:
        if not backup.exists():
            return
        record = json.loads(backup.read_text(encoding='utf-8'))
        with engine.begin() as connection:
            statement = insert(Listing).values(**record)
            connection.execute(statement.on_duplicate_key_update(id=Listing.id))
        backup.unlink()
        print('Original listing restored with its id and timestamp.')
    engine.dispose()


if __name__ == '__main__':
    main()
