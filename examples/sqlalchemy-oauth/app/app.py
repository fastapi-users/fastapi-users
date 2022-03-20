from fastapi import Depends, FastAPI

from app.db import create_db_and_tables
from app.models import UserDB
from app.users import (
    authorization_code_auth_backend,
    current_active_user,
    fastapi_users,
    google_oauth_client,
    password_auth_backend,
)

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(password_auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client, authorization_code_auth_backend, "SECRET"
    ),
    prefix="/auth/google",
    tags=["auth"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: UserDB = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
