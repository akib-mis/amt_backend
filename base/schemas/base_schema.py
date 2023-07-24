from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BaseSchema(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class UpdateBaseSchema(BaseModel):
    updated_at: Optional[datetime]
