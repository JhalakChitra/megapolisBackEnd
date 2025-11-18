from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
<<<<<<< HEAD
from app.database import get_db
from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserOut
from app.security.hashing import Hash
from app.security.jwt_handler import create_access_token
from fastapi import status

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = Hash.bcrypt(user_in.password)
    user = User(email=user_in.email, password=hashed, full_name=user_in.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    if not Hash.verify(user.password, password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token = create_access_token({"user_id": user.id, "email": user.email})
    return {"access_token": token, "token_type": "bearer"}
=======
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
>>>>>>> 082b6d4c510ed30deaf0ac5865cc27e4f383b25f
