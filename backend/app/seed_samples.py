"""python -m app.seed_samples : add 5 sample inventory items for local testing.

Local only, never run on Railway. Delete this file once items can be added in the app (#10).
Safe to run repeatedly.
"""

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import Category, InventoryItem, Location, Product, StockStatus
from app.seed import seed

# (product, category, location slug, status): one of each status, and items outside the fridge
SAMPLES = [
    ("Full cream milk 2L", "Dairy & eggs", "fridge", StockStatus.plenty),
    ("Eggs 12 pack", "Dairy & eggs", "fridge", StockStatus.low),
    ("Butter", "Dairy & eggs", "fridge", StockStatus.out),
    ("Basmati rice 1kg", "Pantry staples", "pantry", StockStatus.low),
    ("Dishwashing liquid", "Cleaning", "cleaning", StockStatus.out),
]


def seed_samples(session: Session) -> None:
    seed(session)  # samples need the locations and categories
    for name, category_name, slug, status in SAMPLES:
        if session.exec(select(Product).where(Product.name == name)).first():
            continue
        location = session.exec(select(Location).where(Location.slug == slug)).one()
        category = session.exec(select(Category).where(Category.name == category_name)).one()
        product = Product(name=name, category_id=category.id, default_location_id=location.id)
        session.add(product)
        session.flush()  # gives product an id without committing yet
        session.add(InventoryItem(product_id=product.id, location_id=location.id, status=status))
    session.commit()


if __name__ == "__main__":
    create_db_and_tables()
    with Session(engine) as session:
        seed_samples(session)
    print("Added sample items.")
