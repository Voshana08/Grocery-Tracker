"""python -m app.seed : seed locations and categories. Safe to run repeatedly."""

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import Category, Location

LOCATIONS = [
    ("Fridge", "fridge"),
    ("Pantry", "pantry"),
    ("Cleaning cupboard", "cleaning"),
]

CATEGORIES = [
    "Fruit & veg",
    "Meat & seafood",
    "Dairy & eggs",
    "Pantry staples",
    "Snacks & drinks",
    "Toiletries",
    "Cleaning",
    "Other",
]


def seed(session: Session) -> None:
    for name, slug in LOCATIONS:
        if not session.exec(select(Location).where(Location.slug == slug)).first():
            session.add(Location(name=name, slug=slug))

    for name in CATEGORIES:
        if not session.exec(select(Category).where(Category.name == name)).first():
            session.add(Category(name=name))

    session.commit()


if __name__ == "__main__":
    create_db_and_tables()
    with Session(engine) as session:
        seed(session)
    print("Seeded locations and categories.")
