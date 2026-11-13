import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy import func, select, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session
from .config import settings
from .database import get_session
from .models import Listing
from .schemas import BulkRequest, BulkResult, CountResponse, Dashboard, ListingPage, Summary

router = APIRouter(prefix='/api')
DB = Annotated[Session, Depends(get_session)]


def require_import_key(x_api_key: Annotated[str | None, Header()] = None):
    if not settings.import_api_key:
        raise HTTPException(503, 'Bulk import is disabled until IMPORT_API_KEY is configured.')
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.import_api_key):
        raise HTTPException(401, 'A valid X-API-Key is required.')


def counts(session, dimension):
    column = getattr(Listing, dimension)
    rows = session.execute(select(column, func.count()).group_by(column)
                           .order_by(func.count().desc(), column)).all()
    items = [{'name': name, 'count': count} for name, count in rows]
    return {'dimension': dimension, 'total': sum(item['count'] for item in items), 'items': items}


def summary(session):
    row = session.execute(select(func.count(Listing.id), func.count(func.distinct(Listing.city)),
        func.count(func.distinct(Listing.category)), func.count(func.distinct(Listing.source)),
        func.count(Listing.phone), func.max(Listing.created_at))).one()
    return dict(zip(['total', 'cities', 'categories', 'sources', 'with_phone', 'latest_import'], row))


@router.get('/health')
def health(session: DB):
    session.execute(text('SELECT 1'))
    # Verify schema readiness, not just the MySQL socket.
    session.execute(select(Listing.id).limit(1))
    return {'status': 'ok', 'database': 'mysql'}


@router.post('/listings/bulk', response_model=BulkResult, dependencies=[Depends(require_import_key)])
def bulk_insert(payload: BulkRequest, session: DB, response: Response):
    unique = {item.fingerprint: {**item.model_dump(), 'fingerprint': item.fingerprint}
              for item in payload.listings}
    statement = insert(Listing).values(list(unique.values()))
    result = session.execute(statement.on_duplicate_key_update(id=Listing.id))
    inserted = result.rowcount
    session.commit()
    response.status_code = 201 if inserted else 200
    return {'received': len(payload.listings), 'inserted': inserted,
            'duplicates': len(payload.listings) - inserted}


@router.get('/analytics/cities', response_model=CountResponse)
def city_counts(session: DB):
    return counts(session, 'city')


@router.get('/analytics/categories', response_model=CountResponse)
def category_counts(session: DB):
    return counts(session, 'category')


@router.get('/analytics/sources', response_model=CountResponse)
def source_counts(session: DB):
    return counts(session, 'source')


@router.get('/summary', response_model=Summary)
def get_summary(session: DB):
    return summary(session)


@router.get('/dashboard', response_model=Dashboard)
def dashboard(session: DB):
    # One transaction provides a coherent MySQL repeatable-read snapshot.
    return {'summary': summary(session), 'cities': counts(session, 'city'),
            'categories': counts(session, 'category'), 'sources': counts(session, 'source')}


@router.get('/listings', response_model=ListingPage)
def listings(session: DB, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
             q: str = Query('', max_length=100), city: str = Query('', max_length=100),
             category: str = Query('', max_length=100)):
    filters = []
    if q.strip():
        # Escape wildcard characters: this is a literal substring search.
        filters.append(Listing.business_name.contains(q.strip(), autoescape=True))
    if city:
        filters.append(Listing.city == city)
    if category:
        filters.append(Listing.category == category)
    total = session.scalar(select(func.count()).select_from(Listing).where(*filters))
    items = session.scalars(select(Listing).where(*filters).order_by(Listing.id)
                            .offset((page - 1) * page_size).limit(page_size)).all()
    return {'total': total, 'items': items, 'page': page, 'page_size': page_size}
