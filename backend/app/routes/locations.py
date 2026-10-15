from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas import LocationOut
from app.services.inventory import get_location_by_slug, list_location_items

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/{slug}", response_model=LocationOut)
def get_location(slug: str, session: Session = Depends(get_session)):
    location = get_location_by_slug(session, slug)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationOut(
        name=location.name, slug=location.slug, items=list_location_items(session, location)
    )
