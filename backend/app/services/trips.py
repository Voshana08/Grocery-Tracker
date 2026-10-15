from datetime import date

from sqlmodel import Session, select

from app.models import Category, Location, Product, ShoppingTrip, Store, TripItem
from app.schemas import TripItemIn, TripItemOut, TripOut
from app.services.inventory import InvalidChoice, get_location_by_slug, get_or_create_product


def trip_total_cents(items: list[TripItem] | list[TripItemOut]) -> int:
    """Trip total = price × quantity over its items. Calculated, never stored."""
    return sum(item.price_cents * item.quantity_bought for item in items)


def create_trip(
    session: Session, store: Store, trip_date: date, items: list[TripItemIn]
) -> TripOut:
    """Save a trip and its items in ONE transaction: if any row is invalid, nothing is saved."""
    try:
        trip = ShoppingTrip(store=store, trip_date=trip_date)
        session.add(trip)
        session.flush()  # gives the trip an id for its items
        for index, row in enumerate(items):
            location = get_location_by_slug(session, row.location_slug)
            if location is None:
                raise InvalidChoice(("items", index, "location_slug"), "Choose where it goes")
            product = get_or_create_product(
                session, row.product_name, row.category_id, location, ("items", index)
            )
            session.add(
                TripItem(
                    trip_id=trip.id,
                    product_id=product.id,
                    location_id=location.id,
                    price_cents=row.price_cents,
                    quantity_bought=row.quantity_bought,
                )
            )
        session.commit()
    except Exception:
        session.rollback()  # undo the trip, its items and any new products
        raise
    return get_trip(session, trip.id)


def get_trip(session: Session, trip_id: int) -> TripOut | None:
    trip = session.get(ShoppingTrip, trip_id)
    if trip is None:
        return None
    rows = session.exec(
        select(TripItem, Product, Category, Location)
        .join(Product, TripItem.product_id == Product.id)
        .join(Category, Product.category_id == Category.id)
        .join(Location, TripItem.location_id == Location.id)
        .where(TripItem.trip_id == trip_id)
        .order_by(TripItem.id)
    ).all()
    items = [
        TripItemOut(
            id=item.id,
            name=product.name,
            category=category.name,
            location=location.name,
            price_cents=item.price_cents,
            quantity_bought=item.quantity_bought,
        )
        for item, product, category, location in rows
    ]
    return TripOut(
        id=trip.id,
        store=trip.store,
        trip_date=trip.trip_date,
        items=items,
        total_cents=trip_total_cents(items),
    )
