import uuid
from typing import Optional
import os
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from base.config import SECRET
from user_acc.models.user_acc import UserApp
from user_acc.services.user_db import get_user_db
from load_dotenv import load_dotenv

load_dotenv()


class UserManager(UUIDIDMixin, BaseUserManager[UserApp, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: UserApp, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        base_dir = os.getenv("AMT_UPLOAD_DIR", "/home/mir/amt_backend/amt_uploads")
        dir_name = f"{user.name}_{str(user.id)[-4:]}"
        # if not os.path.exists(os.path.join(base_dir, dir_name)):
        #     os.mkdir(os.path.join(base_dir, dir_name))
        print(os.path.join(base_dir, dir_name))
        try:
            if not os.path.exists(os.path.join(base_dir, dir_name)):
                os.makedirs(os.path.join(base_dir, dir_name))
                print(
                    f"Directory '{os.path.join(base_dir, dir_name)}' created successfully."
                )
            else:
                print(f"Directory '{os.path.join(base_dir, dir_name)}' already exists.")
        except Exception as e:
            print(f"Error occurred: {e}")

    async def on_after_forgot_password(
        self, user: UserApp, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserApp, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[UserApp, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
