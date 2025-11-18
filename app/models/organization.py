<<<<<<< HEAD
from sqlalchemy import Column, Integer, String, DateTime, func
=======
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
>>>>>>> 082b6d4c510ed30deaf0ac5865cc27e4f383b25f
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    company_website = Column(String, nullable=True)
    name = Column(String, nullable=False)
    address1 = Column(String, nullable=True)
    address2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zipcode = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
=======
    website = Column(String)
    org_name = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    email = Column(String)
    phone = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="organizations")
>>>>>>> 082b6d4c510ed30deaf0ac5865cc27e4f383b25f
