from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas import ItemCreate, LocationItemOut, StatusUpdate
from app.services.inventory import InvalidChoice, add_item, remove_item, set_status

router = APIRouter(tags=["inventory"])


@router.patch("/inventory/{item_id}", response_model=LocationItemOut)
def update_status(item_id: int, update: StatusUpdate, session: Session = Depends(get_session)):
    item = set_status(session, item_id, update.status)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/inventory/{item_id}", status_code=204)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    if not remove_item(session, item_id):
        raise HTTPException(status_code=404, detail="Item not found")


@router.post("/items", response_model=LocationItemOut)
def create_item(new_item: ItemCreate, session: Session = Depends(get_session)):
    try:
        return add_item(
            session,
            new_item.product_name,
            new_item.category_id,
            new_item.location_slug,
            new_item.status,
        )
    except InvalidChoice as error:
        # Same shape as FastAPI's own 422s, so the form can show it next to the right field.
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", *error.loc], "msg": str(error), "type": "value_error"}],
        ) from error
