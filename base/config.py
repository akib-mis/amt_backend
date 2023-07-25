import os
from load_dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv("AMT_DB_USER", "amt")
DB_PASSWORD = os.getenv("AMT_DB_PASSWORD", "mis123")
DB_HOST = os.getenv("AMT_HOST", "localhost")
DB_PORT = os.getenv("AMT_PORT", "5233")
DB_NAME = os.getenv("AMT_DB_NAME", "amt_db")

SECRET = os.getenv(
    "AMT_SECRET",
    "amt92d1aa5f67ce24713cf638550f5daa84ef5ea3466ae29af8b1ad16fbe6c5fbb",
)

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


class Config:
    DB_USER = os.getenv("AMT_DB_USER", "amt")
    DB_PASSWORD = os.getenv("AMT_DB_PASSWORD", "mis123")
    DB_NAME = os.getenv("AMT_DB_NAME", "amt_db")
    DB_HOST = os.getenv("AMT_HOST", "localhost")
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
