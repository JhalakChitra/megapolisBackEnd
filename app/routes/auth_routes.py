from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.user_schema import UserCreate, UserLogin
from app.models.user import User
from app.auth.auth import verify_password, hash_password
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")

    hashed = hash_password(user.password)
    new_user = User(email=user.email, password=hashed)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered"}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid email or password")

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "user": {"id": user.id, "email": user.email}}
