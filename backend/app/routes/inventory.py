from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas import LocationItemOut, StatusUpdate
from app.services.inventory import set_status

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.patch("/{item_id}", response_model=LocationItemOut)
def update_status(item_id: int, update: StatusUpdate, session: Session = Depends(get_session)):
    item = set_status(session, item_id, update.status)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
