from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
from app.database import SessionLocal
from app.schemas.org_schema import OrgCreate
from app.models.organization import Organization
from app.models.user import User
from app.core.config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/organization")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return db.query(User).filter(User.id == user_id).first()
    except:
        raise HTTPException(401, "Invalid token")


@router.post("/create")
def create_org(org: OrgCreate, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)

    new_org = Organization(
        website=org.website,
        org_name=org.org_name,
        address1=org.address1,
        address2=org.address2,
        city=org.city,
        state=org.state,
        zip_code=org.zip_code,
        email=org.email,
        phone=org.phone,
        owner_id=user.id
    )

    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    return new_org


@router.get("/{org_id}")
def get_org(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")
    return org
