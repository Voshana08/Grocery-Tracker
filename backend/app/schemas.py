"""Request and response shapes: the contract between the API and the React front end."""

from pydantic import BaseModel

from app.models import StockStatus


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
