from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50), nullable=False, default="India")
    village = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    mobile = Column(String(15), nullable=False, unique=True, index=True)
    age = Column(Integer, nullable=False)
    work = Column(String(100), nullable=False)
    welcome_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())