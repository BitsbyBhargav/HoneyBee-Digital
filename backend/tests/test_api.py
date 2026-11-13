import pytest
from sqlalchemy.exc import OperationalError
from backend.app.config import settings
from backend.app.database import get_session
from backend.app.main import app


def test_bulk_counts_and_repeat_import(client, headers, records):
    first = client.post('/api/listings/bulk', headers=headers, json={'listings': records + [records[0]]})
    assert first.status_code == 201
    assert first.json() == {'received': 4, 'inserted': 3, 'duplicates': 1}
    again = client.post('/api/listings/bulk', headers=headers, json={'listings': records})
    assert again.status_code == 200
    assert again.json() == {'received': 3, 'inserted': 0, 'duplicates': 3}
    assert client.get('/api/summary').json()['total'] == 3


def test_required_aggregates_reconcile(client, headers, records):
    client.post('/api/listings/bulk', headers=headers, json={'listings': records})
    expected = {'cities': {'Test City A': 2, 'Test City B': 1},
                'categories': {'Cafe': 2, 'Pharmacy': 1},
                'sources': {'Synthetic test fixture': 2, 'Other test fixture': 1}}
    for dimension, values in expected.items():
        response = client.get(f'/api/analytics/{dimension}')
        assert response.status_code == 200
        body = response.json()
        assert body['total'] == sum(item['count'] for item in body['items']) == 3
        assert {item['name']: item['count'] for item in body['items']} == values
    dashboard = client.get('/api/dashboard').json()
    assert dashboard['summary']['total'] == 3
    assert dashboard['summary']['with_phone'] == 1


@pytest.mark.parametrize('field,value', [('business_name', '  '), ('city', ''),
    ('address', ''), ('category', None), ('source_url', 'javascript:alert(1)'), ('phone', 'x' * 101)])
def test_invalid_input_is_atomic(client, headers, records, field, value):
    invalid = {**records[0], field: value}
    response = client.post('/api/listings/bulk', headers=headers, json={'listings': [records[1], invalid]})
    assert response.status_code == 422
    assert client.get('/api/summary').json()['total'] == 0


def test_missing_required_field_and_batch_limits(client, headers, records):
    missing = {key: value for key, value in records[0].items() if key != 'address'}
    for payload in [[], [missing], [records[0]] * 1001]:
        assert client.post('/api/listings/bulk', headers=headers, json={'listings': payload}).status_code == 422


def test_import_is_protected_and_can_be_disabled(client, records, monkeypatch):
    for headers in [{}, {'X-API-Key': 'wrong'}]:
        assert client.post('/api/listings/bulk', headers=headers, json={'listings': records}).status_code == 401
    monkeypatch.setattr(settings, 'import_api_key', '')
    assert client.post('/api/listings/bulk', json={'listings': records}).status_code == 503


def test_normalization_deduplicates_and_missing_phone_is_null(client, headers, records):
    original = records[0]
    duplicate = {**original, 'business_name': '  TEST   ALPHA ', 'phone': ''}
    result = client.post('/api/listings/bulk', headers=headers, json={'listings': [original, duplicate]})
    assert result.json()['inserted'] == 1
    item = client.get('/api/listings').json()['items'][0]
    assert item['phone'] is None
    assert item['business_name'] == 'TEST ALPHA'


def test_search_filters_and_pagination(client, headers, records):
    client.post('/api/listings/bulk', headers=headers, json={'listings': records})
    page = client.get('/api/listings?page=2&page_size=2').json()
    assert page['total'] == 3 and len(page['items']) == 1
    assert client.get('/api/listings?q=alpha').json()['total'] == 1
    assert client.get('/api/listings?city=Test%20City%20A&category=Cafe').json()['total'] == 1
    assert client.get('/api/listings?q=%25').json()['total'] == 0
    assert client.get('/api/listings?page=0').status_code == 422
    assert client.get('/api/listings?page_size=101').status_code == 422


def test_health_empty_dashboard_and_cors(client):
    assert client.get('/api/health').json() == {'status': 'ok', 'database': 'mysql'}
    assert client.get('/api/dashboard').json()['summary']['total'] == 0
    for origin, allowed in [('http://localhost:5173', True), ('https://untrusted.example', False)]:
        response = client.options('/api/listings/bulk', headers={'Origin': origin,
            'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'X-API-Key'})
        assert (response.headers.get('access-control-allow-origin') == origin) == allowed


def test_database_error_is_sanitized(client):
    class BrokenSession:
        def execute(self, *args):
            raise OperationalError('secret statement', {}, Exception('secret connection'))
    app.dependency_overrides[get_session] = lambda: BrokenSession()
    response = client.get('/api/health')
    assert response.status_code == 503
    assert 'secret' not in response.text
