import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import Category, InventoryItem, Location, Product, StockStatus
from app.seed import seed


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed(session)
        yield session


@pytest.fixture
def add_item(session):
    """Returns a function that puts one product in a location with a status."""

    def add(name: str, category: str, slug: str, status: StockStatus) -> InventoryItem:
        location = session.exec(select(Location).where(Location.slug == slug)).one()
        cat = session.exec(select(Category).where(Category.name == category)).one()
        product = Product(name=name, category_id=cat.id, default_location_id=location.id)
        session.add(product)
        session.flush()
        item = InventoryItem(product_id=product.id, location_id=location.id, status=status)
        session.add(item)
        session.commit()
        return item

    return add


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
