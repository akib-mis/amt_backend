from typing import Union

from pydantic import BaseModel


class ContactBase(BaseModel):
    name: Union[str, None] = None
    email: Union[str, None] = None
    phone: str
    mobile: Union[str, None] = None


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int

    class Config:
        orm_mode = True
