from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.schemas import CategoryOut, ProductOut
from app.services.inventory import list_categories, search_products

router = APIRouter(tags=["products"])


@router.get("/categories", response_model=list[CategoryOut])
def get_categories(session: Session = Depends(get_session)):
    return list_categories(session)


@router.get("/products", response_model=list[ProductOut])
def get_products(search: str = "", session: Session = Depends(get_session)):
    return search_products(session, search)
