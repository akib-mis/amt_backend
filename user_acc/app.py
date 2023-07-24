from fastapi import APIRouter

from user_acc.models.user_acc import UserApp as User
from user_acc.routers.user_api import router as user_router

acc_router = APIRouter(
    prefix="/acc",
    responses={404: {"description": "Not found"}},
)

acc_router.include_router(
    user_router,
    tags=["acc"],
)
