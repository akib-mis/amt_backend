from typing import List, Union
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from pydantic import UUID4

from base.db import async_session_maker

from audio_to_midi.models.midi_file_info import FileInfo
from audio_to_midi.schemas.file_schemas import FileCreate, FileUpdate


class FileInfoDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(self, file_info: FileCreate) -> FileUpdate:
        new_file_info = FileInfo(**file_info.dict())
        self.db_session.add(new_file_info)
        await self.db_session.commit()
        await self.db_session.flush()
        return FileUpdate(**new_file_info.__dict__)

    async def get(
        self,
        file_id: Union[int, None] = None,
        file_path: Union[str, None] = None,
        user_id: Union[UUID4, None] = None,
        file_name: Union[str, None] = None,
    ) -> List[FileUpdate]:
        query = select(FileInfo)
        if file_id:
            query = query.where(FileInfo.id == file_id)
        if user_id:
            query = query.where(FileInfo.user_id == user_id)
        if file_path:
            query = query.where(FileInfo.file_path == file_path)
        if file_name:
            query = query.where(FileInfo.file_name == file_name)

        result = await self.db_session.execute(query)
        files = result.scalars().all()
        return [FileUpdate(**f.__dict__) for f in files]

    async def update(
        self,
        file_id: int,
        update_file_info: FileUpdate,
    ) -> FileUpdate:
        q = update(FileInfo).where(FileInfo.id == file_id)
        data_dict = update_file_info.dict(exclude_unset=True)
        q = q.values(**data_dict)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        await self.db_session.commit()
        return FileUpdate(data_dict)


async def get_file_dal():
    async with async_session_maker() as session:
        async with session.begin():
            yield FileInfoDAL(session)
