<<<<<<< HEAD
from sqlalchemy import Column, Integer, String, DateTime, func
=======
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
>>>>>>> 082b6d4c510ed30deaf0ac5865cc27e4f383b25f
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
=======
    email = Column(String, unique=True, index=True)
    password = Column(String)
    fullname = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organizations = relationship("Organization", back_populates="owner")
>>>>>>> 082b6d4c510ed30deaf0ac5865cc27e4f383b25f
