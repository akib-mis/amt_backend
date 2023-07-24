from fastapi import APIRouter

from audio_to_midi.routers.generate_midi_api import gen_midi_router

midi_router = APIRouter(
    prefix="/midi",
    responses={404: {"description": "Not found"}},
)

midi_router.include_router(gen_midi_router, tags=["audio_analysis"])
