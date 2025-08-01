from sqlalchemy.orm import Session
from . import models, schemas, utils
from typing import List, Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# User CRUD

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str = None, phone: str = None, password: str = ""):
    user = None
    if email:
        user = get_user_by_email(db, email)
    elif phone:
        user = get_user_by_phone(db, phone)
    if not user or not utils.verify_password(password, user.hashed_password):
        return None
    return user

# Medication CRUD

def get_medications(db: Session, user_id: int) -> List[models.Medication]:
    return db.query(models.Medication).filter(models.Medication.owner_id == user_id).all()

def create_medication(db: Session, medication: schemas.MedicationCreate, user_id: int) -> models.Medication:
    db_med = models.Medication(
        **medication.dict(exclude_unset=True),
        owner_id=user_id
    )
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med

def update_medication(db: Session, med_id: int, medication_update: schemas.MedicationUpdate) -> Optional[models.Medication]:
    med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not med:
        return None
    update_data = medication_update.dict(exclude_unset=True)
    for var, value in update_data.items():
        setattr(med, var, value)
    db.commit()
    db.refresh(med)
    return med

def delete_medication(db: Session, med_id: int) -> bool:
    med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not med:
        return False
    db.delete(med)
    db.commit()
    return True 