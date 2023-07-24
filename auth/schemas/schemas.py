import uuid
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    email: str


class UserCreate(schemas.BaseUserCreate):
    email: str


class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[str]
