from datetime import UTC, date, datetime

from sqlmodel import select

from app.models import Category, StockStatus, Store
from app.schemas import TripItemIn
from app.services.spending import melbourne_date, month_summary, week_summary
from app.services.trips import create_trip

WEDNESDAY = date(2026, 11, 4)  # the week runs Mon 2 to Sun 8 November


def log_trip(session, day, cents, quantity=1):
    category = session.exec(select(Category)).first()
    item = TripItemIn(
        product_name="Milk",
        category_id=category.id,
        location_slug="fridge",
        price_cents=cents,
        quantity_bought=quantity,
    )
    create_trip(session, Store.aldi, day, [item])


def test_melbourne_date_can_be_a_day_ahead_of_utc():
    # Melbourne is UTC+11 in November, so its day changes at 13:00 UTC.
    assert melbourne_date(datetime(2026, 11, 4, 12, 59, tzinfo=UTC)) == date(2026, 11, 4)
    assert melbourne_date(datetime(2026, 11, 4, 13, 0, tzinfo=UTC)) == date(2026, 11, 5)


def test_month_counts_only_trips_in_this_calendar_month(session):
    log_trip(session, date(2026, 10, 31), 1000)
    log_trip(session, date(2026, 11, 1), 200, quantity=3)
    log_trip(session, date(2026, 11, 30), 50)
    log_trip(session, date(2026, 12, 1), 1000)

    month = month_summary(session, WEDNESDAY)

    assert (month.total_cents, month.trip_count) == (650, 2)


def test_month_with_no_trips_is_zero(session):
    month = month_summary(session, WEDNESDAY)

    assert (month.total_cents, month.trip_count) == (0, 0)


def test_december_rolls_into_the_next_year(session):
    log_trip(session, date(2026, 12, 31), 300)
    log_trip(session, date(2027, 1, 1), 1000)

    assert month_summary(session, date(2026, 12, 15)).total_cents == 300


def test_week_runs_monday_to_sunday(session):
    log_trip(session, date(2026, 11, 1), 1000)  # the Sunday before
    log_trip(session, date(2026, 11, 2), 100)  # Monday
    log_trip(session, date(2026, 11, 2), 200)  # a second trip on Monday
    log_trip(session, date(2026, 11, 8), 400)  # Sunday
    log_trip(session, date(2026, 11, 9), 1000)  # the Monday after

    week = week_summary(session, WEDNESDAY)

    assert (week.total_cents, week.trip_count) == (700, 3)
    assert [day.day.isoformat() for day in week.days] == [
        "2026-11-02",
        "2026-11-03",
        "2026-11-04",
        "2026-11-05",
        "2026-11-06",
        "2026-11-07",
        "2026-11-08",
    ]
    assert [day.trip_count for day in week.days] == [2, 0, 0, 0, 0, 0, 1]


def test_same_week_whichever_day_today_is(session):
    log_trip(session, date(2026, 11, 2), 100)

    assert week_summary(session, date(2026, 11, 2)).trip_count == 1
    assert week_summary(session, date(2026, 11, 8)).trip_count == 1


def test_a_trip_with_several_items_counts_once(session):
    category = session.exec(select(Category)).first()
    items = [
        TripItemIn(
            product_name=name, category_id=category.id, location_slug="fridge", price_cents=100
        )
        for name in ("Milk", "Eggs")
    ]
    create_trip(session, Store.coles, date(2026, 11, 3), items)

    week = week_summary(session, WEDNESDAY)

    assert (week.total_cents, week.trip_count) == (200, 1)


def test_dashboard_lists_low_and_out_items_most_urgent_first(client, add_item):
    add_item("Rice", "Pantry staples", "pantry", StockStatus.out)
    add_item("Yoghurt", "Dairy & eggs", "fridge", StockStatus.low)
    add_item("Apples", "Fruit & veg", "fridge", StockStatus.low)
    add_item("Soap", "Cleaning", "cleaning", StockStatus.low)
    add_item("Milk", "Dairy & eggs", "fridge", StockStatus.plenty)

    data = client.get("/api/dashboard").json()

    assert [(i["name"], i["location"], i["status"]) for i in data["low_and_out"]] == [
        ("Rice", "Pantry", "out"),
        ("Apples", "Fridge", "low"),
        ("Yoghurt", "Fridge", "low"),
        ("Soap", "Cleaning cupboard", "low"),
    ]
    assert len(data["week"]["days"]) == 7
    assert data["month"] == {"total_cents": 0, "trip_count": 0}


def test_locations_count_their_low_and_out_items(client, add_item):
    add_item("Rice", "Pantry staples", "pantry", StockStatus.out)
    add_item("Flour", "Pantry staples", "pantry", StockStatus.low)
    add_item("Sugar", "Pantry staples", "pantry", StockStatus.low)
    add_item("Milk", "Dairy & eggs", "fridge", StockStatus.plenty)

    counts = {
        loc["slug"]: (loc["item_count"], loc["low_count"], loc["out_count"])
        for loc in client.get("/api/locations").json()
    }

    assert counts == {"fridge": (1, 0, 0), "pantry": (3, 2, 1), "cleaning": (0, 0, 0)}
