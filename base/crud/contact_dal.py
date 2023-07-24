from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from base.db import async_session_maker
from base.models.contact import Contact as ContactModel
from base.schemas.contact import Contact, ContactCreate


class ContactDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_contact(self, contact: ContactCreate):
        new_contact = ContactModel(**contact.dict())
        self.db_session.add(new_contact)
        await self.db_session.flush()

    async def get_all_contacts(self) -> List[Contact]:
        q = await self.db_session.execute(
            select(ContactModel).order_by(ContactModel.id)
        )
        return q.scalars().all()

    async def update_contact(
        self,
        contact_id: int,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        mobile: Optional[str],
        website: Optional[str],
    ):
        q = update(ContactModel).where(ContactModel.id == contact_id)
        if name:
            q = q.values(name=name)
        if email:
            q = q.values(email=email)
        if phone:
            q = q.values(phone=phone)
        if mobile:
            q = q.values(mobile=mobile)
        if website:
            q = q.values(websie=website)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)


async def get_contact_dal():
    async with async_session_maker() as session:
        async with session.begin():
            yield ContactDAL(session)
