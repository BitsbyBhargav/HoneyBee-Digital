from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings


class Base(DeclarativeBase):
    pass


# Disabling FOUND_ROWS makes MySQL report 0 for duplicate no-op updates.
engine = create_engine(settings.database_url, pool_pre_ping=True,
                       connect_args={'client_flag': 0, 'connect_timeout': 5})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    with SessionLocal() as session:
        yield session
