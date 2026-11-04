"""Request and response shapes: the contract between the API and the React front end."""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.models import StockStatus, Store

ProductName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class CategoryOut(BaseModel):
    id: int
    name: str


class ProductOut(BaseModel):
    id: int
    name: str
    category_id: int
    default_location_id: int


class LocationSummaryOut(BaseModel):
    id: int
    name: str
    slug: str
    item_count: int
    low_count: int
    out_count: int


class ItemCreate(BaseModel):
    product_name: ProductName
    category_id: int
    location_slug: str
    status: StockStatus = StockStatus.plenty


class LocationItemOut(BaseModel):
    id: int
    name: str
    category: str
    status: StockStatus


class StatusUpdate(BaseModel):
    status: StockStatus


class LocationOut(BaseModel):
    name: str
    slug: str
    items: list[LocationItemOut]


class TripItemIn(BaseModel):
    product_name: ProductName
    category_id: int  # used only when the product is new; a known product keeps its category
    location_slug: str
    price_cents: int = Field(ge=0)
    quantity_bought: int = Field(default=1, ge=1)


class TripCreate(BaseModel):
    store: Store
    trip_date: date
    items: list[TripItemIn] = Field(min_length=1)


class TripItemOut(BaseModel):
    id: int
    name: str
    category: str
    location: str
    price_cents: int
    quantity_bought: int


class TripOut(BaseModel):
    id: int
    store: Store
    trip_date: date
    items: list[TripItemOut]
    total_cents: int  # calculated from the items, never stored


class TripSummaryOut(BaseModel):
    id: int
    store: Store
    trip_date: date
    item_count: int
    total_cents: int


class MonthSummaryOut(BaseModel):
    total_cents: int
    trip_count: int


class DayOut(BaseModel):
    day: date
    trip_count: int


class WeekSummaryOut(BaseModel):
    total_cents: int
    trip_count: int
    days: list[DayOut]  # always 7, Monday to Sunday


class LowItemOut(BaseModel):
    id: int
    name: str
    location: str
    status: StockStatus


class DashboardOut(BaseModel):
    today: date  # in Melbourne, so the page never has to work it out
    month: MonthSummaryOut
    week: WeekSummaryOut
    low_and_out: list[LowItemOut]
