"""Collect bounded, cached OpenStreetMap POI data through the Overpass API."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import requests
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.schemas import ListingInput

CITIES = {
    'Bengaluru': (12.85, 77.48, 13.08, 77.74),
    'Hyderabad': (17.28, 78.30, 17.55, 78.62),
    'Chennai': (12.90, 80.12, 13.18, 80.32),
    'Pune': (18.40, 73.73, 18.65, 73.99),
}
AMENITIES = 'restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream'
ALIASES = {'Bangalore': 'Bengaluru', 'Bengaluru': 'Bengaluru', 'Secunderabad': 'Hyderabad',
           'Hyderabad': 'Hyderabad', 'Chennai': 'Chennai', 'Madras': 'Chennai', 'Pune': 'Pune'}
ENDPOINT = 'https://overpass-api.de/api/interpreter'


def query_for(bbox):
    bounds = ','.join(str(value) for value in bbox)
    return f'''[out:json][timeout:90];
(
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:street"]({bounds});
 nwr["name"]["amenity"~"^({AMENITIES})$"]["addr:street"]({bounds});
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:full"]({bounds});
 nwr["name"]["amenity"~"^({AMENITIES})$"]["addr:full"]({bounds});
);
out tags;'''


def listing_from_element(element, scope_city):
    tags = element.get('tags', {})
    if tags.get('disused') == 'yes' or tags.get('abandoned') == 'yes':
        return None
    category = tags.get('shop') or tags.get('amenity')
    if not category or category in {'vacant', 'no', 'closed', 'disused'}:
        return None
    if not tags.get('addr:full') and not tags.get('addr:street'):
        return None
    # All address components come directly from tags; none are reverse-geocoded or invented.
    address = tags.get('addr:full') or ', '.join(filter(None, [
        tags.get('addr:housenumber'), tags.get('addr:street'), tags.get('addr:suburb'),
        tags.get('addr:city'), tags.get('addr:postcode')]))
    tagged_city = tags.get('addr:city', '')
    city = ALIASES.get(tagged_city, scope_city)
    return ListingInput(business_name=tags.get('name:en') or tags.get('name', ''),
        category=category.replace('_', ' ').title(), city=city, address=address,
        phone=tags.get('contact:phone') or tags.get('phone') or None,
        source='OpenStreetMap', source_url=f"https://www.openstreetmap.org/{element['type']}/{element['id']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Fetch again; default reuses committed raw snapshots.')
    parser.add_argument('--endpoint', default=ENDPOINT)
    args = parser.parse_args()
    raw_dir = ROOT / 'data' / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    records, inputs, rejected, failures = {}, [], Counter(), []
    network_requests = 0
    for city, bbox in CITIES.items():
        query = query_for(bbox)
        query_path = raw_dir / f'{city.lower()}.overpassql'
        raw_path = raw_dir / f'{city.lower()}.json'
        query_path.write_text(query + '\n', encoding='utf-8')
        if raw_path.exists() and not args.refresh:
            payload = json.loads(raw_path.read_text(encoding='utf-8'))
        else:
            if network_requests:
                time.sleep(10)  # Sequential requests with a cooldown; no retry storm on shared servers.
            print(f'Fetching {city} via Overpass API...', flush=True)
            try:
                for attempt in range(2):
                    response = requests.post(args.endpoint, data={'data': query}, timeout=(15, 120),
                        headers={'User-Agent': 'HoneybeeDigitalAssessment/1.0 (educational bounded POI collector)'})
                    if response.status_code in {502, 504} and attempt == 0:
                        print(f'{city}: gateway unavailable; one retry after 30 seconds.', flush=True)
                        time.sleep(30)
                        continue
                    response.raise_for_status()
                    break
                payload = response.json()
            except (requests.RequestException, ValueError) as exc:
                failures.append({'city_scope': city, 'error': str(exc)})
                print(f'{city}: collection unavailable; recording limitation.', flush=True)
                network_requests += 1
                if isinstance(exc, requests.HTTPError) and exc.response.status_code in {403, 429}:
                    print('Access refused or rate limited. Stopping network collection.', flush=True)
                    break
                continue
            if payload.get('remark'):
                raise RuntimeError(f'Overpass reported an incomplete response: {payload["remark"]}')
            raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
            network_requests += 1
        if payload.get('remark'):
            raise RuntimeError('Cached response is incomplete; inspect the raw file.')
        elements = payload.get('elements', [])
        for element in elements:
            try:
                record = listing_from_element(element, city)
            except (ValidationError, KeyError):
                rejected['invalid'] += 1
                continue
            if record is None:
                rejected['missing_required_or_closed'] += 1
            elif record.fingerprint in records:
                rejected['duplicate'] += 1
            else:
                records[record.fingerprint] = record.model_dump()
        inputs.append({'city_scope': city, 'bbox_south_west_north_east': bbox,
                       'raw_file': str(raw_path.relative_to(ROOT)).replace('\\', '/'),
                       'raw_sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest(),
                       'osm_base_timestamp': payload.get('osm3s', {}).get('timestamp_osm_base'),
                       'elements': len(elements)})
        print(f'{city}: {len(elements)} source objects; {len(records)} unique valid listings so far.', flush=True)
    output = sorted(records.values(), key=lambda item: (item['city'], item['business_name'].casefold(), item['address']))
    output_path = ROOT / 'data' / 'listings.json'
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    metadata = {
        'processed_at_utc': datetime.now(timezone.utc).isoformat(),
        'method': 'OpenStreetMap structured POI collection through Overpass API, not HTML scraping',
        'endpoint': args.endpoint, 'source': 'OpenStreetMap contributors', 'licence': 'ODbL 1.0',
        'licence_url': 'https://opendatacommons.org/licenses/odbl/1-0/',
        'attribution_url': 'https://www.openstreetmap.org/copyright',
        'count': len(output), 'synthetic_records': 0,
        'dataset_sha256': hashlib.sha256(output_path.read_bytes()).hexdigest(),
        'counts_by_city': dict(Counter(item['city'] for item in output)),
        'with_phone': sum(bool(item['phone']) for item in output),
        'rejected': dict(rejected), 'inputs': inputs, 'unavailable_scopes': failures,
        'limitations': ['Community POIs may be outdated, incomplete or duplicated.',
            'Street-only addresses are retained as supplied; house numbers and phones may be missing.',
            'City uses a recognised addr:city alias when present; otherwise the bounded collection scope.',
            'Bounding boxes are approximate urban areas, not municipal boundary checks.',
            'No business ownership, current operation or telephone verification was performed.'],
    }
    (ROOT / 'data' / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(f'Saved {len(output)} sourced records; {metadata["with_phone"]} have a supplied phone.')
    if len(output) < 500:
        raise SystemExit('Dataset is below 500; report this limitation, do not fabricate records.')


if __name__ == '__main__':
    main()
