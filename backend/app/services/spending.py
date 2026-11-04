from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlmodel import Session, func, select

from app.models import ShoppingTrip, TripItem
from app.schemas import DayOut, MonthSummaryOut, WeekSummaryOut

MELBOURNE = ZoneInfo("Australia/Melbourne")


def melbourne_date(moment: datetime) -> date:
    """The calendar day in Melbourne at this moment (it can differ from the UTC day)."""
    return moment.astimezone(MELBOURNE).date()


def _trips_by_day(session: Session, start: date, end: date) -> dict[date, tuple[int, int]]:
    """{day: (trip count, total cents)} for days from start up to, but not including, end."""
    rows = session.exec(
        select(
            ShoppingTrip.trip_date,
            func.count(ShoppingTrip.id.distinct()),
            func.sum(TripItem.price_cents * TripItem.quantity_bought),
        )
        .join(TripItem, TripItem.trip_id == ShoppingTrip.id)
        .where(ShoppingTrip.trip_date >= start, ShoppingTrip.trip_date < end)
        .group_by(ShoppingTrip.trip_date)
    ).all()
    return {day: (count, total) for day, count, total in rows}


def month_summary(session: Session, today: date) -> MonthSummaryOut:
    """Total spend and trip count for the calendar month that today is in."""
    first = today.replace(day=1)
    next_month = (first + timedelta(days=31)).replace(day=1)
    days = _trips_by_day(session, first, next_month).values()
    return MonthSummaryOut(
        total_cents=sum(total for _, total in days),
        trip_count=sum(count for count, _ in days),
    )


def week_summary(session: Session, today: date) -> WeekSummaryOut:
    """The Monday-to-Sunday week that today is in, with every day listed for the week row."""
    monday = today - timedelta(days=today.weekday())
    by_day = _trips_by_day(session, monday, monday + timedelta(days=7))
    week = [monday + timedelta(days=offset) for offset in range(7)]
    return WeekSummaryOut(
        total_cents=sum(total for _, total in by_day.values()),
        trip_count=sum(count for count, _ in by_day.values()),
        days=[DayOut(day=day, trip_count=by_day.get(day, (0, 0))[0]) for day in week],
    )
