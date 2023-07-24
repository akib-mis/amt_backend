from sqlalchemy import Column, String

from base.db import Base, BaseModel, User


class UserApp(User, Base, BaseModel):
    __table_args__ = {"extend_existing": True}
    name = Column(String(100))
    display_name = Column(String(100))
