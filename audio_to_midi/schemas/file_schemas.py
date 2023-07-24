from pydantic import BaseModel, UUID4
from base.schemas.base_schema import BaseSchema, UpdateBaseSchema
from typing import Optional, List


class FileCreate(BaseSchema):
    file_name: str
    file_path: str
    user_id: UUID4
    is_complete: Optional[bool]


class FileUpdate(UpdateBaseSchema):
    id: Optional[int]
    file_name: Optional[str]
    file_path: Optional[str]
    is_complete: Optional[bool]
