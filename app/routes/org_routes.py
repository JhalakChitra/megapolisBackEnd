from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.organization import Organization
from app.schemas.org_schemas import OrgCreate, OrgOut
from typing import List

router = APIRouter()

@router.post("/", response_model=OrgOut)
def create_org(org_in: OrgCreate, db: Session = Depends(get_db)):
    org = Organization(**org_in.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

@router.get("/", response_model=List[OrgOut])
def list_orgs(db: Session = Depends(get_db)):
    orgs = db.query(Organization).all()
    return orgs
