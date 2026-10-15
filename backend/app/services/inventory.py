from sqlmodel import Session, select

from app.models import Category, InventoryItem, Location, Product, StockStatus, utc_now
from app.schemas import LocationItemOut


def get_location_by_slug(session: Session, slug: str) -> Location | None:
    return session.exec(select(Location).where(Location.slug == slug)).first()


def _items_with_names():
    """Inventory items joined to their product (for the name) and category."""
    return (
        select(InventoryItem, Product, Category)
        .join(Product, InventoryItem.product_id == Product.id)
        .join(Category, Product.category_id == Category.id)
    )


def _to_out(item: InventoryItem, product: Product, category: Category) -> LocationItemOut:
    return LocationItemOut(
        id=item.id, name=product.name, category=category.name, status=item.status
    )


def list_location_items(session: Session, location: Location) -> list[LocationItemOut]:
    rows = session.exec(
        _items_with_names().where(InventoryItem.location_id == location.id).order_by(Product.name)
    ).all()
    return [_to_out(*row) for row in rows]


def set_status(session: Session, item_id: int, status: StockStatus) -> LocationItemOut | None:
    """Change one item's stock status. Returns None if the item doesn't exist."""
    row = session.exec(_items_with_names().where(InventoryItem.id == item_id)).first()
    if row is None:
        return None
    item = row[0]
    item.status = status
    item.updated_at = utc_now()
    session.add(item)
    session.commit()
    return _to_out(*row)
