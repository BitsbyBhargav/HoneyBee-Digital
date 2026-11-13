"""Read-only MySQL evidence for the assessment video. Prints no credentials."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.database import engine


def table(headers, rows):
    values = [[str(value) if value is not None else 'NULL' for value in row] for row in rows]
    widths = [max(len(header), *(len(row[i]) for row in values)) if values else len(header)
              for i, header in enumerate(headers)]
    print(' | '.join(header.ljust(widths[i]) for i, header in enumerate(headers)))
    print('-+-'.join('-' * width for width in widths))
    for row in values:
        print(' | '.join(value.ljust(widths[i]) for i, value in enumerate(row)))


def main():
    with engine.connect() as connection:
        database, version, port = connection.exec_driver_sql('SELECT DATABASE(), VERSION(), @@port').one()
        print(f'MySQL {version} | Database: {database} | Server port: {port}')
        print('\nSQL> SHOW TABLES;')
        table(['Table'], connection.exec_driver_sql('SHOW TABLES').all())
        print('\nSQL> DESCRIBE listing_master;')
        columns = connection.exec_driver_sql('DESCRIBE listing_master').all()
        table(['Column', 'Type', 'Nullable', 'Key'], [row[:4] for row in columns])
        print('\nSQL> SELECT COUNT(*) FROM listing_master;')
        print('Total stored listings:', connection.exec_driver_sql('SELECT COUNT(*) FROM listing_master').scalar())
        print('\nSQL> SELECT id, business_name, category, city, source FROM listing_master ORDER BY id LIMIT 5;')
        table(['ID', 'Business name', 'Category', 'City', 'Source'], connection.exec_driver_sql(
            'SELECT id, business_name, category, city, source FROM listing_master ORDER BY id LIMIT 5').all())
        print('\nSQL> SELECT city, COUNT(*) FROM listing_master GROUP BY city ORDER BY COUNT(*) DESC;')
        table(['City', 'Listings'], connection.exec_driver_sql(
            'SELECT city, COUNT(*) FROM listing_master GROUP BY city ORDER BY COUNT(*) DESC').all())
    print('\nRead-only demonstration complete. No rows were changed.')


if __name__ == '__main__':
    main()
