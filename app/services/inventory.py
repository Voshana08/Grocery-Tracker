from sqlmodel import Session, select

from app.models import Location


def get_location_by_slug(session: Session, slug: str) -> Location | None:
    return session.exec(select(Location).where(Location.slug == slug)).first()
