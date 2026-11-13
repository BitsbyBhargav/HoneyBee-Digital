"""Compare live API aggregates, MySQL rows and the checked-in dataset."""
from collections import Counter
import json
from pathlib import Path
import sys
import requests
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.database import SessionLocal
from backend.app.models import Listing
from backend.app.schemas import ListingInput


def main():
    records = json.loads((ROOT / 'data' / 'listings.json').read_text(encoding='utf-8'))
    expected = {ListingInput.model_validate(record).fingerprint for record in records}
    with SessionLocal() as session:
        actual = set(session.scalars(select(Listing.fingerprint)).all())
    assert expected == actual, 'MySQL rows differ from the dataset.'
    response = requests.get('http://127.0.0.1:8000/api/dashboard', timeout=30)
    response.raise_for_status()
    dashboard = response.json()
    assert dashboard['summary']['total'] == len(records)
    for plural, field in [('cities', 'city'), ('categories', 'category'), ('sources', 'source')]:
        response = requests.get(f'http://127.0.0.1:8000/api/analytics/{plural}', timeout=30)
        response.raise_for_status()
        analytics = response.json()
        expected_counts = dict(Counter(record[field] for record in records))
        assert {row['name']: row['count'] for row in analytics['items']} == expected_counts
        assert analytics['total'] == sum(expected_counts.values()) == len(records)
        assert analytics == dashboard[plural]
    report = {'mysql_count': len(actual), 'dataset_count': len(records),
              'dataset_fingerprints_match': True, 'all_three_aggregations_match': True,
              'summary': dashboard['summary']}
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'docs' / 'live-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
