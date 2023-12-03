import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from base.app import app
from base.db import create_db_and_tables
from user_acc.app import acc_router
from auth.app import auth_router as jwt_auth
from audio_to_midi.app import midi_router

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:8010",
    "http://localhost:3000",
    "http://localhost:3030",
    "http://localhost:3009",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(acc_router)
app.include_router(jwt_auth)
app.include_router(midi_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to AMT",
    }


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
