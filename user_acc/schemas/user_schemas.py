from typing import Optional

from auth.schemas.schemas import UserCreate as UsrCreate
from auth.schemas.schemas import UserRead as UsrRead
from auth.schemas.schemas import UserUpdate as UsrUpdate


class UserRead(UsrRead):
    name: Optional[str]
    display_name: Optional[str]


class UserCreate(UsrCreate):
    name: Optional[str]
    display_name: Optional[str]


class UserUpdate(UsrUpdate):
    display_name: Optional[str]
    name: Optional[str]
