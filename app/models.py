from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    village = Column(String, nullable=False)
    mobile = Column(String, nullable=False, unique=True, index=True)
    age = Column(Integer, nullable=False)
    work = Column(String, nullable=False)
    welcome_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())