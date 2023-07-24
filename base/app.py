from fastapi import FastAPI

from auth.services.auth_service import fastapi_users

app = FastAPI(title="AMT", version="2023.06.12")

# Get the current user (active or not)
current_user = fastapi_users.current_user()

# Get the current active user
current_active_user = fastapi_users.current_user(active=True)

# Get the current active and verified user
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)

# Get the current active superuser
current_superuser = fastapi_users.current_user(active=True, superuser=True)
