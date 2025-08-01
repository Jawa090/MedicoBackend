import os
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from jose import jwt
import httpx
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

router = APIRouter(prefix="/auth", tags=["auth"])

async def verify_google_token(token: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://www.googleapis.com/oauth2/v3/certs")
        jwks = resp.json()
    try:
        unverified_header = jwt.get_unverified_header(token)
        key = next(k for k in jwks["keys"] if k["kid"] == unverified_header["kid"])
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=GOOGLE_CLIENT_ID,
            issuer="https://accounts.google.com"
        )
        return payload
    except Exception:
        return None

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.email and crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.phone and crud.get_user_by_phone(db, user.phone):
        raise HTTPException(status_code=400, detail="Phone already registered")
    db_user = crud.create_user(db, user)
    return db_user

@router.post("/login", response_model=schemas.UserOut)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_data.email, login_data.phone, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@router.post("/google", response_model=schemas.UserOut)
async def google_auth(token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    payload = await verify_google_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    email = payload.get("email")
    name = payload.get("name")
    picture = payload.get("picture")
    user = crud.get_user_by_email(db, email)
    if not user:
        user_in = schemas.UserCreate(
            name=name or email.split("@")[0],
            email=email,
            phone=None,
            password=os.urandom(16).hex()
        )
        user = crud.create_user(db, user_in)
        if picture:
            user.profile_image = picture
            db.commit()
            db.refresh(user)
    return schemas.UserOut.model_validate(user, from_attributes=True)

@router.post("/update-fcm-token", response_model=schemas.UserOut)
def update_fcm_token(user_id: int = Body(...), fcm_token: str = Body(...), db: Session = Depends(get_db)):
    user = crud.update_fcm_token(db, user_id, fcm_token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me", response_model=schemas.UserOut)
def get_me():
    return schemas.UserOut(
        id=1,
        email="test@example.com",
        name="Test User",
        phone=None,
        join_date="2023-01-01T00:00:00Z",
        profile_image=None
    ) 