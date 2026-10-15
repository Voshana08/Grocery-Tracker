from sqlmodel import Session, select

from app.models import Category, InventoryItem, Location, Product
from app.schemas import LocationItemOut


def get_location_by_slug(session: Session, slug: str) -> Location | None:
    return session.exec(select(Location).where(Location.slug == slug)).first()


def list_location_items(session: Session, location: Location) -> list[LocationItemOut]:
    rows = session.exec(
        select(InventoryItem, Product, Category)
        .join(Product, InventoryItem.product_id == Product.id)
        .join(Category, Product.category_id == Category.id)
        .where(InventoryItem.location_id == location.id)
        .order_by(Product.name)
    ).all()
    return [
        LocationItemOut(id=item.id, name=product.name, category=category.name, status=item.status)
        for item, product, category in rows
    ]
