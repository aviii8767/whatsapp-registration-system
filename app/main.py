from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from . import models
from .database import engine, get_db

# looks at every class that inherits from Base & create matching table in registrations.db
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]
    field = first_error["loc"][-1]  # which field failed
    message = first_error["msg"] # why it failed
    return JSONResponse(
        status_code=422,
        content={"detail": f"{field}: {message}"},
    )

# Makes everything inside the "static" folder reachable in the browser,
# e.g. static/register.html becomes http://localhost:8000/static/register.html
app.mount("/static", StaticFiles(directory="static"), name="static")


class RegistrationIn(BaseModel):
    name: str = Field(min_length=1)
    village: str = Field(min_length=1)
    mobile: str = Field(min_length=10, max_length=15)
    age: int = Field(gt=0, lt=120)
    work: str = Field(min_length=1)

    @field_validator("mobile")
    @classmethod
    def mobile_must_be_digits(cls, v):
        if not v.isdigit():
            raise ValueError("Mobile number must contain digit only")
        return v


@app.get("/")
def root():
    return FileResponse("static/register.html")

@app.post("/register")
def register(payload: RegistrationIn, db: Session = Depends(get_db)):
    record = models.Registration(
        name=payload.name,
        village=payload.village,
        mobile=payload.mobile,
        age=payload.age,
        work=payload.work,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="This mobile number is already registered.")
    db.refresh(record)
    return {"id": record.id, "message": "Registered successfully."}

@app.get("/admin/registrations")
def list_registrations(db: Session = Depends(get_db)):
    rows = db.query(models.Registration).all()
    return [
        {"id": r.id, "name": r.name, "village": r.village, "mobile": r.mobile,
         "age": r.age, "work": r.work, "crated_at": r.created_at}
         for r in rows
    ]
