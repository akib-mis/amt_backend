from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    Float,
    String,
    ForeignKey,
    Date,
    DateTime,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from base.db import Base, BaseModel
from user_acc.models.user_acc import UserApp


class FileInfo(BaseModel, Base):
    __tablename__ = "midi_file_info"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    file_path = Column(String, index=True)
    user = relationship("FileUser", back_populates="user_file")
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    is_complete = Column(Boolean, default=False)


class FileUser(UserApp):
    user_file = relationship("FileInfo", back_populates="user")
