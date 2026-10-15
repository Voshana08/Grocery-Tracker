from sqlmodel import Session, func, select

from app.models import Category, InventoryItem, Location, Product, StockStatus, utc_now
from app.schemas import LocationItemOut


class InvalidChoice(ValueError):
    """A form value that points at something that doesn't exist (e.g. an unknown category)."""

    def __init__(self, loc: tuple, message: str):
        super().__init__(message)
        self.loc = loc  # path to the field, e.g. ("category_id",) or ("items", 2, "location_slug")


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


def list_locations(session: Session) -> list[Location]:
    return session.exec(select(Location).order_by(Location.id)).all()


def list_categories(session: Session) -> list[Category]:
    return session.exec(select(Category).order_by(Category.id)).all()


def search_products(session: Session, search: str = "") -> list[Product]:
    query = select(Product).order_by(Product.name)
    if search.strip():
        query = query.where(func.lower(Product.name).contains(search.strip().lower()))
    return session.exec(query).all()


def find_product(session: Session, name: str) -> Product | None:
    """Look up a product by name, ignoring capitals ("butter" finds "Butter")."""
    return session.exec(select(Product).where(func.lower(Product.name) == name.lower())).first()


def get_or_create_product(
    session: Session, name: str, category_id: int, location: Location, loc: tuple = ()
) -> Product:
    """The product with this name (ignoring capitals), or a new one in this category.
    loc is where category_id came from, for the error if it doesn't exist."""
    product = find_product(session, name)
    if product is None:
        if session.get(Category, category_id) is None:
            raise InvalidChoice((*loc, "category_id"), "Choose a category")
        product = Product(name=name, category_id=category_id, default_location_id=location.id)
        session.add(product)
        session.flush()  # gives the new product an id
    return product


def add_item(
    session: Session, product_name: str, category_id: int, location_slug: str, status: StockStatus
) -> LocationItemOut:
    """Put a product in a location. Reuses an existing product with the same name; if that
    product is already in the location, its status is updated instead of adding a duplicate."""
    location = get_location_by_slug(session, location_slug)
    if location is None:
        raise InvalidChoice(("location_slug",), "Choose a location")
    product = get_or_create_product(session, product_name, category_id, location)

    item = session.exec(
        select(InventoryItem).where(
            InventoryItem.product_id == product.id, InventoryItem.location_id == location.id
        )
    ).first()
    if item is None:
        item = InventoryItem(product_id=product.id, location_id=location.id, status=status)
    else:
        item.status = status
        item.updated_at = utc_now()
    session.add(item)
    session.commit()
    return _to_out(item, product, session.get(Category, product.category_id))
