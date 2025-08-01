from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Time, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    profile_image = Column(String, nullable=True)
    join_date = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('phone', name='uq_user_phone'),
    )
    medications = relationship("Medication", back_populates="owner")

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    dosage = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    amount_type = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    days = Column(String, nullable=False)  # CSV of day names (e.g., "Monday,Tuesday,Wednesday")
    time = Column(String, nullable=False)  # e.g., "08:00"
    end_date = Column(Date, nullable=True)
    color = Column(String, nullable=False, default="blue")
    taken = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="medications") 