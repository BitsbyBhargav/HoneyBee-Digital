import secrets
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import dotenv_values
from backend.app.config import ROOT, settings
from backend.app.database import Base, get_session
from backend.app.main import app


@pytest.fixture(scope='session')
def mysql_test_engine():
    password = dotenv_values(ROOT / '.env').get('MYSQL_ROOT_PASSWORD')
    name = 'honeybee_test_' + secrets.token_hex(6)
    admin = create_engine(settings.database_url.set(username='root', password=password, database=None))
    with admin.begin() as connection:
        connection.exec_driver_sql(f'CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
    test_engine = create_engine(settings.database_url.set(username='root', password=password, database=name),
                               connect_args={'client_flag': 0})
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()
    with admin.begin() as connection:
        # Only the newly generated test database is removed.
        connection.exec_driver_sql(f'DROP DATABASE `{name}`')
    admin.dispose()


@pytest.fixture
def client(mysql_test_engine):
    connection = mysql_test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode='create_savepoint')
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def headers():
    return {'X-API-Key': settings.import_api_key}


@pytest.fixture
def records():
    return [
        {'business_name': 'Test Alpha', 'category': 'Cafe', 'city': 'Test City A',
         'address': '1 Test Street', 'phone': None, 'source': 'Synthetic test fixture'},
        {'business_name': 'Test Beta', 'category': 'Cafe', 'city': 'Test City B',
         'address': '2 Test Street', 'phone': '+91 0000000000', 'source': 'Synthetic test fixture'},
        {'business_name': 'Test Gamma', 'category': 'Pharmacy', 'city': 'Test City A',
         'address': '3 Test Street', 'phone': None, 'source': 'Other test fixture'},
    ]
