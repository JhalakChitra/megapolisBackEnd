from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
from app.database import SessionLocal
from app.schemas.org_schema import OrgCreate
from app.models.organization import Organization
from app.models.user import User
from app.core.config import SECRET_KEY, ALGORITHM
from pydantic import BaseModel
from fastapi import APIRouter
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re
import json

router = APIRouter()

# Request body model
class URLRequest(BaseModel):
    url: str


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











@router.post("/scrape-website")
def scrape_website(data: URLRequest):
    url = data.url
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Organization name
        org_name = soup.title.string.strip() if soup.title else ""
        if not org_name:
            h1 = soup.find("h1")
            org_name = h1.text.strip() if h1 else ""

        # Emails
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", response.text)
        email = emails[0] if emails else ""

        # Phones
        phones = re.findall(r"\+?\d[\d\s.-]{7,}\d", response.text)
        phone = phones[0] if phones else ""

        # Address info
        address1 = ""
        city = ""
        state = ""
        zip_code = ""

        # 1️⃣ Check <address> tag
        addr_tag = soup.find("address")
        if addr_tag:
            text = " ".join(addr_tag.stripped_strings)
        else:
            # 2️⃣ Check common address classes
            possible = soup.find_all(
                lambda tag: tag.name in ["p", "div", "span"] and 
                tag.get("class") and any("address" in c.lower() for c in tag.get("class"))
            )
            text = " ".join(possible[0].stripped_strings) if possible else ""

        # 3️⃣ JSON-LD structured data
        scripts = soup.find_all("script", type="application/ld+json")
        for s in scripts:
            try:
                data_json = json.loads(s.string)
                if isinstance(data_json, dict):
                    addr = data_json.get("address")
                    if addr:
                        address1 = addr.get("streetAddress", address1)
                        city = addr.get("addressLocality", city)
                        state = addr.get("addressRegion", state)
                        zip_code = addr.get("postalCode", zip_code)
            except:
                continue

        # 4️⃣ If text exists but JSON-LD didn't give details, try to parse
        if text and not address1:
            # Split by commas and try to find parts
            parts = [p.strip() for p in text.split(",") if p.strip()]
            if len(parts) >= 3:
                address1 = parts[0]
                city = parts[1]
                # Assume last part has state + zip
                state_zip = parts[-1].split()
                if len(state_zip) >= 2:
                    state = state_zip[0]
                    zip_code = state_zip[1]
                elif len(state_zip) == 1:
                    state = state_zip[0]
            elif len(parts) == 2:
                address1 = parts[0]
                city = parts[1]
            elif len(parts) == 1:
                address1 = parts[0]

        return {
            "organizationName": org_name,
            "email": email,
            "phone": phone,
            "address1": address1,
            "city": city,
            "state": state,
            "zipCode": zip_code
        }

    except Exception as e:
        print("Scraping error:", e)
        return {
            "organizationName": "",
            "email": "",
            "phone": "",
            "address1": "",
            "city": "",
            "state": "",
            "zipCode": ""
        }
