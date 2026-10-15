"""Request and response shapes: the contract between the API and the React front end."""

from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.models import StockStatus

ProductName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class CategoryOut(BaseModel):
    id: int
    name: str


class ProductOut(BaseModel):
    id: int
    name: str
    category_id: int


class LocationSummaryOut(BaseModel):
    name: str
    slug: str


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
