from typing import List

import aiohttp
from fastapi import APIRouter, Depends

from base.app import current_superuser
from base.crud.contact_dal import ContactDAL, get_contact_dal
from base.schemas.contact import Contact as sContact
from base.schemas.contact import ContactCreate

router = APIRouter(
    prefix="/base",
    tags=["base"],
    responses={404: {"description": "Not found"}},
)


@router.post("/contact", dependencies=[Depends(current_superuser)])
async def create_contact(
    contact: ContactCreate, contact_dal: ContactDAL = Depends(get_contact_dal)
):
    return await contact_dal.create_contact(contact)


@router.get("/contacts")
async def get_all_contacts(
    contact_dal: ContactDAL = Depends(get_contact_dal),
) -> List[sContact]:
    return await contact_dal.get_all_contacts()


async def task():
    url = "http://103.123.168.54:1214"
    headers = {
        "url": url,
        "db": "agrim_db_v3",
        "username": "admin",
        "Content-Type": "application/json",
        "token": "057518dc01ce6bc00f0e40b6d7c5bf4333ef2cc9",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f"{url}/api/get_employee", json={}) as response:

            print("Status:", response.status)
            print("Content-type:", response.headers["content-type"])
            res = await response.json()
            # employees = res["result"].get("response") # or employees = res["result"]["response"]
            # better to use get method for dict as follows
            result = res.get("result")
            employees = list()
            if result:
                employees = result.get("response")
                return employees
            return None


@router.get("/test")
async def get_test():
    return await task()
