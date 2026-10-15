from datetime import UTC, date, datetime

import pytest
from sqlmodel import select

from app.models import (
    Category,
    InventoryItem,
    Location,
    Product,
    ShoppingTrip,
    StockStatus,
    Store,
    TripItem,
)
from app.schemas import TripItemIn
from app.services.inventory import InvalidChoice
from app.services.trips import create_trip, trip_total_cents


def category_id(session, name):
    return session.exec(select(Category).where(Category.name == name)).one().id


def row(session, name, category, slug, cents, quantity=1):
    return TripItemIn(
        product_name=name,
        category_id=category_id(session, category),
        location_slug=slug,
        price_cents=cents,
        quantity_bought=quantity,
    )


def test_trip_total_is_price_times_quantity():
    items = [TripItem(price_cents=450, quantity_bought=2), TripItem(price_cents=99)]
    assert trip_total_cents(items) == 999


def test_create_trip_saves_the_trip_and_its_items(session, add_item):
    add_item("Butter", "Dairy & eggs", "fridge", StockStatus.out)

    trip = create_trip(
        session,
        Store.coles,
        date(2026, 10, 15),
        [
            row(session, "butter", "Other", "fridge", 550),  # existing product, any capitals
            row(session, "Basmati rice 1kg", "Pantry staples", "pantry", 325, quantity=2),
        ],
    )

    assert (trip.store, trip.trip_date, trip.total_cents) == ("Coles", date(2026, 10, 15), 1200)
    assert [(i.name, i.category, i.location, i.price_cents) for i in trip.items] == [
        ("Butter", "Dairy & eggs", "Fridge", 550),  # kept its own category
        ("Basmati rice 1kg", "Pantry staples", "Pantry", 325),
    ]
    assert len(session.exec(select(Product)).all()) == 2


def test_a_bad_row_saves_nothing(session):
    with pytest.raises(InvalidChoice) as error:
        create_trip(
            session,
            Store.aldi,
            date(2026, 10, 15),
            [
                row(session, "New thing", "Other", "fridge", 100),
                row(session, "Another", "Other", "garage", 200),
            ],
        )

    assert error.value.loc == ("items", 1, "location_slug")
    assert session.exec(select(ShoppingTrip)).all() == []
    assert session.exec(select(TripItem)).all() == []
    assert session.exec(select(Product)).all() == []  # "New thing" was rolled back too


def trip_body(session, **changes):
    body = {
        "store": "Woolworths",
        "trip_date": "2026-10-15",
        "items": [
            {
                "product_name": "Full cream milk 2L",
                "category_id": category_id(session, "Dairy & eggs"),
                "location_slug": "fridge",
                "price_cents": 310,
            }
        ],
    }
    return {**body, **changes}


def test_post_trip_returns_it_with_total_and_it_can_be_read_back(client, session):
    response = client.post("/api/trips", json=trip_body(session))

    assert response.status_code == 200
    trip = response.json()
    assert (trip["store"], trip["total_cents"], trip["items"][0]["quantity_bought"]) == (
        "Woolworths",
        310,
        1,
    )
    assert client.get(f"/api/trips/{trip['id']}").json() == trip


@pytest.mark.parametrize(
    ("changes", "where"),
    [
        ({"store": "IGA"}, ["body", "store"]),
        ({"trip_date": ""}, ["body", "trip_date"]),
        ({"items": []}, ["body", "items"]),
    ],
)
def test_post_trip_refuses_a_bad_store_date_or_no_items(client, session, changes, where):
    response = client.post("/api/trips", json=trip_body(session, **changes))

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == where


def test_post_trip_errors_say_which_row_and_field(client, session):
    body = trip_body(session)
    body["items"].append({**body["items"][0], "price_cents": -1})
    body["items"].append({**body["items"][0], "location_slug": "garage"})

    negative = client.post("/api/trips", json=body)
    assert negative.status_code == 422
    assert negative.json()["detail"][0]["loc"] == ["body", "items", 1, "price_cents"]

    body["items"].pop(1)
    unknown_place = client.post("/api/trips", json=body)
    assert unknown_place.status_code == 422
    assert unknown_place.json()["detail"][0]["loc"] == ["body", "items", 1, "location_slug"]


def test_unknown_trip_is_404(client):
    assert client.get("/api/trips/999").status_code == 404


def stock(session, product_name, slug):
    """Status of a product in a location, or None if it isn't tracked there."""
    row = session.exec(
        select(InventoryItem)
        .join(Product, InventoryItem.product_id == Product.id)
        .join(Location, InventoryItem.location_id == Location.id)
        .where(Product.name == product_name, Location.slug == slug)
    ).first()
    return row.status if row else None


def test_saving_a_trip_restocks_items_already_at_home(session, add_item):
    butter = add_item("Butter", "Dairy & eggs", "fridge", StockStatus.out)
    butter.updated_at = datetime(2026, 1, 1, tzinfo=UTC)
    session.add(butter)
    session.commit()

    create_trip(
        session, Store.coles, date(2026, 10, 15), [row(session, "Butter", "Other", "fridge", 550)]
    )

    session.refresh(butter)
    assert butter.status == StockStatus.plenty
    assert butter.updated_at > datetime(2026, 1, 1, tzinfo=UTC)


def test_saving_a_trip_adds_new_items_to_where_they_went(session, add_item):
    add_item("Butter", "Dairy & eggs", "fridge", StockStatus.low)

    create_trip(
        session,
        Store.aldi,
        date(2026, 10, 15),
        [
            row(session, "Butter", "Other", "pantry", 550),  # known product, new place this time
            row(session, "Dishwashing liquid", "Cleaning", "cleaning", 399),  # brand-new product
        ],
    )

    assert stock(session, "Butter", "pantry") == StockStatus.plenty
    assert stock(session, "Butter", "fridge") == StockStatus.low  # other places untouched
    assert stock(session, "Dishwashing liquid", "cleaning") == StockStatus.plenty


def test_a_failed_trip_restocks_nothing(session, add_item):
    add_item("Butter", "Dairy & eggs", "fridge", StockStatus.out)

    with pytest.raises(InvalidChoice):
        create_trip(
            session,
            Store.aldi,
            date(2026, 10, 15),
            [
                row(session, "Butter", "Other", "fridge", 550),
                row(session, "Anything", "Other", "garage", 100),
            ],
        )

    assert stock(session, "Butter", "fridge") == StockStatus.out


def test_trips_list_is_newest_first_with_counts_and_totals(client, session):
    def log(store, day, prices):
        body = trip_body(session, store=store, trip_date=day)
        body["items"] = [{**body["items"][0], "price_cents": cents} for cents in prices]
        return client.post("/api/trips", json=body).json()["id"]

    older = log("Aldi", "2026-10-10", [500, 250])
    newer = log("Coles", "2026-10-14", [999])
    same_day_later = log("Woolworths", "2026-10-14", [100, 100, 100])

    trips = client.get("/api/trips").json()

    assert [(t["id"], t["store"], t["item_count"], t["total_cents"]) for t in trips] == [
        (same_day_later, "Woolworths", 3, 300),
        (newer, "Coles", 1, 999),
        (older, "Aldi", 2, 750),
    ]


def test_trips_list_is_empty_before_any_trip(client):
    assert client.get("/api/trips").json() == []
