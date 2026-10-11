from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .config import BASE_DIR
from .database import get_db
from .security import require_admin

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@router.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.post("/register")
def register(payload: schemas.RegistrationIn, db: Session = Depends(get_db)):
    record = models.Registration(**payload.model_dump())
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="This mobile number is already registered.")
    db.refresh(record)
    return {"id": record.id, "message": "Registered successfully."}


@router.get(
    "/admin/list_registrations",
    response_class=HTMLResponse,
    dependencies=[Depends(require_admin)],
)
def list_registrations(request: Request, db: Session = Depends(get_db)):
    rows = db.query(models.Registration).order_by(models.Registration.id.desc()).all()
    return templates.TemplateResponse(request, "registrations_list.html", {"rows": rows})