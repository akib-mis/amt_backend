from typing import List, Union

from fastapi_users.password import PasswordHelper
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from base.db import async_session_maker
from sqlalchemy import desc, update
from user_acc.app import User
from user_acc.schemas.user_schemas import UserRead, UserCreate, UserUpdate


class UserDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get(
        self,
        user_id: Union[UUID4, None] = None,
        user_email: Union[str, None] = None,
    ) -> List[UserRead]:
        query = select(User)
        if user_id:
            query = query.where(User.id == user_id)
        if user_email:
            query = query.where(User.email == user_email)
        result = await self.db_session.execute(query)
        users = result.scalars().all()
        return [UserRead(**u.__dict__) for u in users]

    async def update(
        self,
        user: UserUpdate,
        user_id: Union[UUID4, None] = None,
        user_email: Union[str, None] = None,
    ):
        if user_id:
            q = update(User).where(User.id == user_id)
        elif user_email:
            q = update(User).where(User.email == user_email)
        else:
            return {}
        data_dict = user.dict(exclude_unset=True)
        q = q.values(**data_dict)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        await self.db_session.commit()
        await self.db_session.flush()
        return data_dict

    async def change_password(
        self,
        user_id: UUID4,
        new_password: str,
        current_password: Union[str, None] = None,
    ):
        p = PasswordHelper()
        if current_password:
            q = await self.db_session.execute(select(User).where(User.id == user_id))
            users = q.scalars().all()
            if not users:
                return False
            db_pass = users[0].hashed_password
            verified, _ = p.verify_and_update(current_password, db_pass)
            if not verified:
                return False
        hashed_password = p.hash(new_password)
        q = update(User).where(User.id == user_id)
        q = q.values(hashed_password=hashed_password)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        await self.db_session.commit()
        return True


async def get_user_dal():
    async with async_session_maker() as session:
        async with session.begin():
            yield UserDAL(session)
