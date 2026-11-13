import hashlib
import unicodedata
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


def clean_text(value: str) -> str:
    return ' '.join(unicodedata.normalize('NFKC', value).split())


class ListingInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    business_name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=1000)
    phone: str | None = Field(default=None, max_length=100)
    source: str = Field(min_length=1, max_length=100)
    source_url: str | None = Field(default=None, max_length=500)

    @field_validator('*', mode='before')
    @classmethod
    def normalize(cls, value):
        return clean_text(value) if isinstance(value, str) else value

    @field_validator('phone')
    @classmethod
    def empty_phone(cls, value):
        return value or None

    @field_validator('source_url')
    @classmethod
    def safe_url(cls, value):
        if value is not None and not value.startswith(('https://', 'http://')):
            raise ValueError('source_url must use http or https')
        return value

    @property
    def fingerprint(self):
        parts = [self.business_name, self.city, self.address]
        return hashlib.sha256('\x1f'.join(p.casefold() for p in parts).encode()).hexdigest()


class BulkRequest(BaseModel):
    listings: list[ListingInput] = Field(min_length=1, max_length=1000)


class BulkResult(BaseModel):
    received: int
    inserted: int
    duplicates: int


class ListingOutput(ListingInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class ListingPage(BaseModel):
    items: list[ListingOutput]
    total: int
    page: int
    page_size: int


class CountItem(BaseModel):
    name: str
    count: int


class CountResponse(BaseModel):
    dimension: str
    total: int
    items: list[CountItem]


class Summary(BaseModel):
    total: int
    cities: int
    categories: int
    sources: int
    with_phone: int
    latest_import: datetime | None


class Dashboard(BaseModel):
    summary: Summary
    cities: CountResponse
    categories: CountResponse
    sources: CountResponse
