from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models import utc_now
from app.schemas import DashboardOut
from app.services.inventory import low_and_out_items
from app.services.spending import melbourne_date, month_summary, week_summary

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardOut)
def get_dashboard(session: Session = Depends(get_session)):
    today = melbourne_date(utc_now())
    return DashboardOut(
        today=today,
        month=month_summary(session, today),
        week=week_summary(session, today),
        low_and_out=low_and_out_items(session),
    )
