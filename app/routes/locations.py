from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from app.database import get_session
from app.services.inventory import get_location_by_slug
from app.templating import templates

router = APIRouter()


@router.get("/t/{slug}", response_class=HTMLResponse)
def location_page(slug: str, request: Request, session: Session = Depends(get_session)):
    location = get_location_by_slug(session, slug)
    if location is None:
        return templates.TemplateResponse(
            request, "location_not_found.html", {"slug": slug}, status_code=404
        )
    return templates.TemplateResponse(request, "location.html", {"location": location, "items": []})
