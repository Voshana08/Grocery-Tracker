from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class StockStatus(str, Enum):
    plenty = "plenty"
    low = "low"
    out = "out"


class Location(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(unique=True, index=True)


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    category_id: int = Field(foreign_key="category.id")
    default_location_id: int = Field(foreign_key="location.id")
    image_url: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)


class InventoryItem(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("product_id", "location_id"),)

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    location_id: int = Field(foreign_key="location.id")
    status: StockStatus = Field(default=StockStatus.plenty)
    quantity: float | None = Field(default=None)
    unit: str | None = Field(default=None)
    updated_at: datetime = Field(default_factory=utc_now)
