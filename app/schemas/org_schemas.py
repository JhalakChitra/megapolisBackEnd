from pydantic import BaseModel, EmailStr
from typing import Optional

class OrgCreate(BaseModel):
    company_website: Optional[str] = None
    name: str
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class OrgOut(BaseModel):
    id: int
    name: str
    company_website: Optional[str]
    email: Optional[EmailStr]

    class Config:
        orm_mode = True
