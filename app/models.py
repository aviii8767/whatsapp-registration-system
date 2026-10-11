from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from .database import Base

# Field limits: shared by the table and by validation in schemas.py
NAME_MAX = 100
COUNTRY_MAX = 50
VILLAGE_MAX = 100
STATE_MAX = 50
DISTRICT_MAX = 50
MOBILE_MAX = 15
WORK_MAX = 100


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(NAME_MAX), nullable=False, comment="Identify the person")
    age = Column(Integer, nullable=False, comment="Basic personal information")
    mobile = Column(
        String(MOBILE_MAX), nullable=False, unique=True, index=True,
        comment="WhatsApp contact number",
    )
    work = Column(String(WORK_MAX), nullable=False, comment="Occupation or profession")
    village = Column(String(VILLAGE_MAX), nullable=False, comment="Local address")
    district = Column(String(DISTRICT_MAX), nullable=False, comment="Larger location")
    state = Column(String(STATE_MAX), nullable=False, comment="State-level location")
    country = Column(
        String(COUNTRY_MAX), nullable=False, default="India",
        comment="Country; defaults to India",
    )

    welcome_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())