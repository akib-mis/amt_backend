from typing import List, Union, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from user_acc.app import User
from user_acc.services.app_user import current_active_verified_user as app_verified_user
from audio_to_midi.schemas.pitch_schemas import PitchData, PitchInfo
from audio_to_midi.services.midi_gen_service import MidiGenerator
from audio_to_midi.services.file_service import FileService
import os

gen_midi_router = APIRouter(
    prefix="/midi_generate",
    responses={404: {"description": "Not found"}},
)


@gen_midi_router.get(
    "/download",
    dependencies=[Depends(app_verified_user)],
    status_code=status.HTTP_200_OK,
)
async def download_file(
    user: User = Depends(app_verified_user),
    file_id: Union[int, None] = None,
    file_path: Union[str, None] = None,
    file_name: Union[str, None] = None,
):
    try:
        file_service = FileService(user=user)
        resp = await file_service.get_files(
            file_id=file_id,
            file_path=file_path,
            file_name=file_name,
        )
        if len(resp) == 1:
            resp = resp[0]
            complete_path = os.path.join(resp.file_path, resp.file_name)
            if not os.path.exists(complete_path):
                return JSONResponse(
                    content={
                        "message": "File doesnot exists",
                        "location": "download_file",
                    },
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            print(resp.file_name)
            return FileResponse(
                path=complete_path,
                media_type="application/octet-stream",
                headers={"Content-Disposition": f'inline; filename="{resp.file_name}"'},
            )
        else:
            return resp
    except Exception as e:
        return JSONResponse(
            content={
                "message": "File download error",
                "error": str(e),
                "location": "download_file",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@gen_midi_router.post(
    "/pitch",
    dependencies=[Depends(app_verified_user)],
    status_code=status.HTTP_201_CREATED,
)
async def generate_pitch_to_midi(
    pitch_data: List[PitchData],
    name: Union[str, None] = None,
    user: User = Depends(app_verified_user),
):
    try:
        midi_gen = MidiGenerator(user=user)
        midi_gen.create_midi_from_pitch(pitch_data=pitch_data)
        resp = await midi_gen.save_midi(name=name)
        return resp
    except Exception as e:
        return JSONResponse(
            content={
                "message": "File midi generation error",
                "error": str(e),
                "location": "generate_pitch_to_midi",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@gen_midi_router.post(
    "/audio",
    dependencies=[Depends(app_verified_user)],
    status_code=status.HTTP_201_CREATED,
)
async def upload_and_save_audio(
    file: UploadFile = File(...),
    user: User = Depends(app_verified_user),
    name: Union[str, None] = None,
):
    if not file.filename.endswith((".mp3", ".m4a", ".mid", ".midi", ".wav")):
        return JSONResponse(
            content={"message": "invalid file type"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    midi_gen = MidiGenerator(user=user)
    try:
        resp = await midi_gen.save_audio(file=file, name=name)
        return resp
    except Exception as e:
        return JSONResponse(
            content={
                "message": "error in saving file",
                "error": str(e),
                "location": "upload_and_save_audio",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@gen_midi_router.post(
    "/notes",
    dependencies=[Depends(app_verified_user)],
    status_code=status.HTTP_201_CREATED,
)
async def generate_note_to_midi(
    audio_path: str,
    name: Union[str, None] = None,
    user: User = Depends(app_verified_user),
    tempo: Optional[int] = 22,
):
    try:
        midi_gen = MidiGenerator(user=user)
        midi_gen.audio_to_midi(audio_path=audio_path, tempo=tempo)
        if not name:
            name = audio_path.split(".")[0]
        resp = await midi_gen.save_midi(name=name)
        return resp
    except Exception as e:
        return JSONResponse(
            content={
                "message": "File midi generation error",
                "error": str(e),
                "location": "generate_pitch_to_midi",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# @gen_midi_router.get("",dependencies=[Depends(app_verified_user)],status_code=status.HTTP_200_OK)
# # async def
