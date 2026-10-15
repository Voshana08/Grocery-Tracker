from datetime import UTC, date, datetime
from enum import Enum

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class StockStatus(str, Enum):
    plenty = "plenty"
    low = "low"
    out = "out"


class Store(str, Enum):
    woolworths = "Woolworths"
    coles = "Coles"
    aldi = "Aldi"
    other = "Other"


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


class ShoppingTrip(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    store: Store
    trip_date: date  # the day the user shopped, chosen in the form
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)


class TripItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="shoppingtrip.id", index=True)
    product_id: int = Field(foreign_key="product.id")
    location_id: int = Field(foreign_key="location.id")  # where it went this time
    price_cents: int  # always whole cents: $4.50 is 450
    quantity_bought: int = Field(default=1)
