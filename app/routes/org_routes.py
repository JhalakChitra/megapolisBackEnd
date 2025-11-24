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
async def scrape_website(data: dict):
    import requests
    from bs4 import BeautifulSoup
    import re

    url = data.get("url")
    if not url.startswith("http"):
        url = "http://" + url

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla"})
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)
    except Exception as e:
        return {"error": f"Failed to fetch website: {str(e)}"}

    # -------------------------------
    # ORG NAME
    # -------------------------------
    title = soup.title.string if soup.title else ""
    org_name = title.split("|")[0].split("-")[0].strip()

    # -------------------------------
    # EMAIL
    # -------------------------------
    email = ""
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if emails:
        email = emails[0]

    # -------------------------------
    # PHONE (supports all countries)
    # -------------------------------
    phone_regex = r"\+?\d[\d\-\s\(\)]{7,20}\d"
    phones = re.findall(phone_regex, text)
    phone = phones[0] if phones else ""

    # -------------------------------
    # 🌍 UNIVERSAL ADDRESS EXTRACTION
    # -------------------------------
    address_block = ""

    # 1) Try tags first
    for tag in soup.find_all(["p", "div", "li", "section", "footer"]):
        txt = tag.get_text(" ", strip=True)

        # must contain numbers + letters → real address
        if re.search(r"\d", txt) and len(txt) > 20 and len(txt) < 300:
            
            # must have street/road or city/state clues
            if any(word in txt.lower() for word in [
                "road", "street", "st", "lane", "nagar", "sector", "tower",
                "city", "district", "province", "state", "floor",
                "ave", "avenue", "blvd", "drive", "dr", "suite", "office"
            ]):
                address_block = txt
                break

    # 2) REGEX fallback — global support
    if not address_block:
        patterns = [

            # INDIA
            r"\d{1,4}[A-Za-z0-9 ,.'\-]+(Road|Street|Nagar|Colony|Lane|Sector)[A-Za-z0-9 ,.'\-]+",

            # USA / CANADA
            r"\d{1,5}\s+[A-Za-z0-9 ,.'\-]+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)[A-Za-z0-9 ,.'\-]+",
            r"[A-Za-z ]+,\s?[A-Z]{2}\s?\d{5}(-\d{4})?",

            # UK
            r"[A-Za-z0-9 ,.'\-]+ (London|Manchester|Birmingham|Leeds)[A-Za-z0-9 ,.'\-]+",
            r"[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}",

            # AUSTRALIA
            r"[A-Za-z ]+,\s?(NSW|VIC|QLD|SA|WA|TAS|ACT)\s?\d{4}",

            # Europe
            r"\d{4,5}\s+[A-Za-z ]+,\s?[A-Za-z ]+",

            # UAE / Gulf
            r"P\.?O\.? Box\s?\d{3,6}"
        ]

        for p in patterns:
            m = re.search(p, text)
            if m:
                address_block = m.group()
                break

    # ------------------------------------
    # CITY, STATE, ZIP EXTRACTION
    # ------------------------------------
    city = ""
    state = ""
    zip_code = ""

    if address_block:

        # universal ZIP (4–6 digit)
        zip_m = re.search(r"\b\d{4,6}\b", address_block)
        if zip_m:
            zip_code = zip_m.group()

        # split by comma
        parts = [p.strip() for p in address_block.split(",") if p.strip()]

        if len(parts) >= 3:
            city = parts[-3]
            state = parts[-2]
        elif len(parts) == 2:
            city = parts[0]
            state = parts[1]

    return {
        "organizationName": org_name,
        "email": email,
        "phone": phone,
        "address1": address_block,
        "city": city,
        "state": state,
        "zipCode": zip_code,
    }


