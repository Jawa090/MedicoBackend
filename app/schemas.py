from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import date, datetime

class MedicationBase(BaseModel):
    name: str
    dosage: str
    amount: str
    amount_type: str
    frequency: str
    days: str
    time: str
    end_date: Optional[date] = None
    color: Optional[str] = "blue"
    taken: Optional[bool] = False

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(BaseModel):
    taken: Optional[bool]
    # Add other updatable fields as needed

class Medication(MedicationBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    # Accepts any phone number with digits, spaces, dashes, parentheses, or plus sign
    phone: Optional[constr(pattern=r'^[\d\s\-\+\(\)]+$')] = None
    fcm_token: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

class UserOut(UserBase):
    id: int
    join_date: datetime
    profile_image: Optional[str] = None
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 