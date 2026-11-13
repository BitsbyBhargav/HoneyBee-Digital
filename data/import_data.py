"""Import the validated dataset through the protected FastAPI endpoint."""
import argparse
import json
from pathlib import Path
import sys
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.config import settings
from backend.app.schemas import ListingInput


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    parser.add_argument('--file', type=Path, default=ROOT / 'data' / 'listings.json')
    args = parser.parse_args()
    records = [ListingInput.model_validate(item).model_dump()
               for item in json.loads(args.file.read_text(encoding='utf-8'))]
    totals = {'received': 0, 'inserted': 0, 'duplicates': 0}
    for offset in range(0, len(records), 500):
        response = requests.post(f'{args.url.rstrip("/")}/api/listings/bulk',
            json={'listings': records[offset:offset + 500]},
            headers={'X-API-Key': settings.import_api_key}, timeout=60)
        response.raise_for_status()
        result = response.json()
        for key in totals:
            totals[key] += result[key]
    print(json.dumps(totals, indent=2))


if __name__ == '__main__':
    main()
