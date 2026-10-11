import os
import secrets
from fastapi import status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from html import escape
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse

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
    country: str = Field(default="India")
    village: str = Field(min_length=1)
    state: str = Field(min_length=1)
    district: str = Field(min_length=1)
    mobile: str = Field(min_length=1)
    age: int = Field(gt=0, lt=120)
    work: str = Field(min_length=1)

    @field_validator("mobile")
    @classmethod
    def mobile_must_be_digits(cls, v):
        if not v.isdigit():
            raise ValueError("Mobile number must contain digit only")
        if len(v) != 10:
            raise ValueError("Mobile number must be exactly 10 digits")
        return v


security = HTTPBasic()


def require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    admin_user = os.getenv("ADMIN_USER")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_user or not admin_password:
        raise HTTPException(status_code=500, detail="Admin login is not configured.")

    user_ok = secrets.compare_digest(credentials.username.encode(), admin_user.encode())
    pass_ok = secrets.compare_digest(credentials.password.encode(), admin_password.encode())
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

    
@app.get("/")
def root():
    return FileResponse("static/register.html")

@app.post("/register")
def register(payload: RegistrationIn, db: Session = Depends(get_db)):
    record = models.Registration(
        name=payload.name,
        country=payload.country,
        village=payload.village,
        state=payload.state,
        district=payload.district,
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

@app.get("/admin/list_registrations", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def list_registrations(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Registration)
        .order_by(models.Registration.id.desc())
        .all()
    )

    table_rows = ""
    for r in rows:
        table_rows += (
            "<tr>"
            f'<td data-label="ID">{r.id}</td>'
            f'<td data-label="Name">{escape(r.name)}</td>'
            f'<td data-label="Village">{escape(r.village)}</td>'
            f'<td data-label="District">{escape(r.district)}</td>'
            f'<td data-label="State">{escape(r.state)}</td>'
            f'<td data-label="Mobile">{escape(r.mobile)}</td>'
            f'<td data-label="Age">{r.age}</td>'
            f'<td data-label="Work">{escape(r.work)}</td>'
            f'<td data-label="Registered">{r.created_at:%d %b %Y, %I:%M %p}</td>'
            "</tr>"
        )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Registrations</title>
      <style>
        body {{ font-family: sans-serif; padding: 16px; background: #f5f5f5; }}
        .wrap {{ overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; background: #fff; }}
        th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
        th {{ background: #128C7E; color: #fff; }}
        tbody tr:nth-child(even) {{ background: #f9f9f9; }}

        @media (max-width: 700px) {{
          table, tbody, tr, td {{ display: block; }}
          thead {{ display: none; }}
          tr {{ background: #fff !important; margin-bottom: 12px; border: 1px solid #ddd;
                border-radius: 8px; padding: 6px 10px; }}
          td {{ border: none; padding: 6px 0; display: flex;
                justify-content: space-between; gap: 12px; text-align: right;
                overflow-wrap: anywhere; }}
          td::before {{ content: attr(data-label); font-weight: bold;
                        color: #128C7E; text-align: left; }}
        }}
      </style>
    </head>
    <body>
      <h2>Registrations ({len(rows)})</h2>
      <div class="wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Name</th><th>Village</th><th>District</th><th>State</th>
              <th>Mobile</th><th>Age</th><th>Work</th><th>Registered</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </div>
    </body>
    </html>
    """