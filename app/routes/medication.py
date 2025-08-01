from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from .. import crud, models, schemas, database

router = APIRouter(prefix="/medications", tags=["medications"])

DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _med_to_schema(med):
    # Do not convert days to a list; leave as string for schema
    data = med.__dict__.copy()
    return schemas.Medication(**data)

@router.get("/", response_model=List[schemas.Medication])
def list_medications(owner_id: int = Query(..., description="User ID to filter medications by owner"), db: Session = Depends(get_db)):
    meds = db.query(models.Medication).filter(models.Medication.owner_id == owner_id).all()
    return [_med_to_schema(med) for med in meds]

@router.post("/", response_model=schemas.Medication)
def add_medication(medication: schemas.MedicationCreate, owner_id: int, db: Session = Depends(get_db)):
    db_med = models.Medication(
        name=medication.name,
        dosage=medication.dosage,
        amount=medication.amount,
        amount_type=medication.amount_type,
        frequency=medication.frequency,
        days=medication.days,
        time=medication.time,
        end_date=medication.end_date,
        color=medication.color,
        taken=medication.taken,
        owner_id=owner_id
    )
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return _med_to_schema(db_med)

@router.patch("/{med_id}", response_model=schemas.Medication)
def update_medication(med_id: int, medication_update: schemas.MedicationUpdate, db: Session = Depends(get_db)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    update_data = medication_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(med, key, value)
    db.commit()
    db.refresh(med)
    return _med_to_schema(med)

@router.delete("/{med_id}")
def delete_medication(med_id: int, db: Session = Depends(get_db)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    db.delete(med)
    db.commit()
    return {"ok": True} 