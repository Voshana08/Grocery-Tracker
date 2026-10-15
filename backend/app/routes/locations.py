from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas import LocationOut, LocationSummaryOut
from app.services.inventory import get_location_by_slug, list_location_items, list_locations

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationSummaryOut])
def get_locations(session: Session = Depends(get_session)):
    return list_locations(session)


@router.get("/{slug}", response_model=LocationOut)
def get_location(slug: str, session: Session = Depends(get_session)):
    location = get_location_by_slug(session, slug)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationOut(
        name=location.name, slug=location.slug, items=list_location_items(session, location)
    )
