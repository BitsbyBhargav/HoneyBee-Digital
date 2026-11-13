import pytest
from data.collect import listing_from_element


def test_collector_preserves_source_values_without_inventing_address():
    element = {'type': 'node', 'id': 123, 'tags': {'name': 'Test Cafe', 'amenity': 'cafe',
               'addr:street': 'Test Road', 'addr:city': 'Bangalore'}}
    listing = listing_from_element(element, 'Bengaluru')
    assert listing.address == 'Test Road, Bangalore'
    assert listing.city == 'Bengaluru'
    assert listing.phone is None
    assert listing.source_url == 'https://www.openstreetmap.org/node/123'


@pytest.mark.parametrize('tags', [{'name': 'No address', 'shop': 'bakery'},
    {'name': 'Closed', 'shop': 'vacant', 'addr:street': 'Test Street'},
    {'name': 'Disused', 'shop': 'bakery', 'addr:street': 'Test Street', 'disused': 'yes'}])
def test_collector_excludes_incomplete_or_closed_objects(tags):
    assert listing_from_element({'type': 'node', 'id': 1, 'tags': tags}, 'Pune') is None
