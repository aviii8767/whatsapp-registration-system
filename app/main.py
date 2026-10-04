from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from . import models
from .database import engine, get_db

# looks at every class that inherits from Base & create matching table in registrations.db
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Makes everything inside the "static" folder reachable in the browser,
# e.g. static/register.html becomes http://localhost:8000/static/register.html
app.mount("/static", StaticFiles(directory="static"), name="static")


class RegistrationIn(BaseModel):
    name: str = Field(min_length=1)
    village: str = Field(min_length=1)
    mobile: str = Field(min_length=10, max_length=15)
    age: int = Field(gt=0, lt=120)
    work: str = Field(min_length=1)


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
