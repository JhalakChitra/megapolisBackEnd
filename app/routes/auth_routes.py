from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.user_schema import UserCreate, UserLogin
from app.models.user import User
from app.auth.auth import verify_password, hash_password
from app.auth.jwt_handler import create_access_token
from app.schemas.user_schema import ForgotPasswordRequest





router = APIRouter(prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @router.post("/register")
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     existing = db.query(User).filter(User.email == user.email).first()
#     if existing:
#         raise HTTPException(400, "Email already exists")

#     hashed = hash_password(user.password)
#     new_user = User(email=user.email, password=hashed)

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return {"message": "User registered"}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid email or password")

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "user": {"id": user.id, "email": user.email}}






@router.post("/send-verify-email")
def send_verify_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

    # Generate token
    token = create_email_token({"email": email}, expires_minutes=30)

    # Frontend verify link
    verify_link = f"http://localhost:5173/verify-email?token={token}"

    # Send email
    send_email(
        to_email=email,
        subject="Verify Your Email - Megapolis",
        html_body=f"<h2>Email Verification</h2><p>Click below:</p><a href='{verify_link}'>Verify Email</a>"
    )

    return {"message": "Verification mail sent"}







@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    data = decode_email_token(token)

    if not data:
        raise HTTPException(400, "Invalid or expired token")

    email = data.get("email")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

    user.is_active = True
    db.commit()

    return {"message": "Email verified successfully"}



@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        email = data.email
        user = db.query(User).filter(User.email == email).first()

        # For security, do not reveal if email exists
        if not user:
            return {"message": "If email exists, reset link sent"}

        # Create token
        token = create_email_token({"email": email}, expires_minutes=10)

        reset_link = f"http://localhost:5173/reset-password?token={token}"

        send_email(
            to_email=email,
            subject="Reset Password - Megapolis",
            html_body=f"<h2>Reset Password</h2><a href='{reset_link}'>Reset Password</a>"
        )

        return {"message": "Reset link sent"}
    except Exception as e:
        # debug 500 errors
        return {"error": str(e)}








@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    data = decode_email_token(token)

    if not data:
        raise HTTPException(400, "Invalid or expired token")

    email = data.get("email")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

    # Hash new password
    user.password = hash_password(new_password)

    db.commit()

    return {"message": "Password updated successfully"}
