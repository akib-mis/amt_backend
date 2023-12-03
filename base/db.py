import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

from base.config import DATABASE_URL
from base.models.base_model import BaseModel

Base: DeclarativeMeta = declarative_base()


# class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
#     pass


class User(SQLAlchemyBaseUserTableUUID, Base, BaseModel):
    __table_args__ = {"extend_existing": True}

    # oauth_accounts: List[OAuthAccount] = relationship("OAuthAccount", lazy="joined")
    id = Column(
        UUID(as_uuid=True),
        unique=True,
        index=True,
        primary_key=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    email = Column(String(100), unique=True, index=True)


engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as db:
        yield db


async def create_db_and_tables():
    print(engine.url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


# code session generator


def async_session_generator():
    return sessionmaker(engine, class_=AsyncSession)


@asynccontextmanager
async def get_code_session():
    try:
        async_session = async_session_generator()

        async with async_session() as session:
            yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
