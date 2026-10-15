from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas import TripCreate, TripOut, TripSummaryOut
from app.services.inventory import InvalidChoice
from app.services.trips import create_trip, get_trip, list_trips

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("", response_model=list[TripSummaryOut])
def read_trips(session: Session = Depends(get_session)):
    return list_trips(session)


@router.post("", response_model=TripOut)
def log_trip(new_trip: TripCreate, session: Session = Depends(get_session)):
    try:
        return create_trip(session, new_trip.store, new_trip.trip_date, new_trip.items)
    except InvalidChoice as error:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", *error.loc], "msg": str(error), "type": "value_error"}],
        ) from error


@router.get("/{trip_id}", response_model=TripOut)
def read_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = get_trip(session, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
