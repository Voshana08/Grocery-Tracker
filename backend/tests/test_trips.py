from datetime import date

import pytest
from sqlmodel import select

from app.models import Category, Product, ShoppingTrip, StockStatus, Store, TripItem
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
