from pydantic import BaseModel

class OrgCreate(BaseModel):
    website: str
    org_name: str
    address1: str
    address2: str
    city: str
    state: str
    zip_code: str
    email: str
    phone: str

class OrgResponse(BaseModel):
    id: int
    website: str
    org_name: str
    address1: str
    address2: str
    city: str
    state: str
    zip_code: str
    email: str
    phone: str

    class Config:
        orm_mode = True
