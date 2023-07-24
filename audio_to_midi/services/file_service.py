from audio_to_midi.crud.file_info_dal import get_file_dal
from typing import Union, List
from user_acc.app import User
import os
from pydantic import UUID4
from fastapi.responses import JSONResponse
from fastapi import status
from audio_to_midi.schemas.file_schemas import FileCreate, FileUpdate


class FileService:
    def __init__(self, user: User) -> None:
        self.user = user
        self._get_path_of_user()

    def _get_path_of_user(self):
        base_dir = os.getenv(
            "AMT_UPLOAD_DIR", "/home/akib/Desktop/AI_projects/AMT_uploads"
        )
        self.user_dir = os.path.join(
            base_dir,
            f"{self.user.name}_{str(self.user.id)[-4:]}",
        )

    async def get_files(
        self,
        file_id: Union[int, None] = None,
        file_path: Union[str, None] = None,
        file_name: Union[str, None] = None,
    ) -> List[FileUpdate]:
        try:
            file_info_gen = get_file_dal()
            file_dal = await file_info_gen.__anext__()
            resp = await file_dal.get(
                file_id=file_id,
                file_name=file_name,
                user_id=self.user.id,
                file_path=file_path,
            )
            return resp
        except Exception as e:
            return JSONResponse(
                content={
                    "message": "File information retrival error",
                    "error": str(e),
                    "location": "get_files",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def update(
        self,
        file_id: int,
        update_file_info: FileUpdate,
    ) -> FileUpdate:
        try:
            file_info_gen = get_file_dal()
            file_dal = await file_info_gen.__anext__()
            resp = await file_dal.update(
                file_id=file_id, update_file_info=update_file_info
            )
            return resp
        except Exception as e:
            return JSONResponse(
                content={
                    "message": "File information updation error",
                    "error": str(e),
                    "location": "get_files",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def create(self, file_info: FileCreate) -> FileUpdate:
        try:
            file_info_gen = get_file_dal()
            file_dal = await file_info_gen.__anext__()
            resp = await file_dal.create(file_info=file_info)
            return resp
        except Exception as e:
            return JSONResponse(
                content={
                    "message": "File information creation error",
                    "error": str(e),
                    "location": "get_files",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
