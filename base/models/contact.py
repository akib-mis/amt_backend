from sqlalchemy import Boolean, Column, Integer, String

from base.db import Base

# from sqlalchemy.orm import relationship


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    mobile = Column(String)
    website = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
