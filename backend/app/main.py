import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .config import settings
from .routes import router

app = FastAPI(title='Business Listings API', version='1.0.0',
              description='MySQL-backed listings and reproducible directory analytics.')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_methods=['GET', 'POST'], allow_headers=['Content-Type', 'X-API-Key'])
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    # Do not echo a potentially large or sensitive input payload in an error.
    errors = [{'location': list(error['loc']), 'message': error['msg'], 'type': error['type']}
              for error in exc.errors()]
    return JSONResponse(status_code=422, content={'detail': errors})


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError):
    logging.getLogger(__name__).error('Database operation failed: %s', type(exc).__name__)
    return JSONResponse(status_code=503, content={'detail': 'Database unavailable. Check MySQL and run database setup.'})
