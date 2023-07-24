from user_acc.services.app_user import auth_backend
from user_acc.schemas.user_schemas import UserCreate, UserRead, UserUpdate
from fastapi import APIRouter, Depends, status, Response
from user_acc.services.app_user import fastapi_users
from fastapi.responses import JSONResponse
from user_acc.crud.user_dal import UserDAL, get_user_dal
from base.app import current_superuser
from typing import List, Union
from pydantic import UUID4


router = APIRouter(
    prefix="/users",
)


router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt")
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth/jwt")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(current_superuser)],
)
async def get_users(
    user_id: Union[UUID4, None] = None,
    user_email: Union[str, None] = None,
    user_dal: UserDAL = Depends(get_user_dal),
):
    try:
        return await user_dal.get(user_id=user_id, user_email=user_email)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "User data retrival error",
                "Error": str(e),
                "location": "get_users",
            },
        )


@router.post(
    "/forgot_password",
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    employee_id: int,
    new_password: str,
    user_dal: UserDAL = Depends(get_user_dal),
):
    try:
        res = await user_dal.change_password(
            employee_id=employee_id,
            new_password=new_password,
        )
        if res:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "detail": "Successfully password updated",
                },
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Incorrect Password",
                },
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Bad password reset request", "errors": str(e)},
        )
