from typing import Type

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import Response

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUser, Models
from fastapi_users.password import get_password_hash


def get_user_router(
    user_db: BaseUserDatabase, user_model: Type[BaseUser], auth: BaseAuthentication
) -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()
    models = Models(user_model)

    @router.post("/register", response_model=models.User)
    async def register(user: models.UserCreate):  # type: ignore
        hashed_password = get_password_hash(user.password)
        db_user = models.UserDB(**user.dict(), hashed_password=hashed_password)
        created_user = await user_db.create(db_user)
        return created_user

    @router.post("/login")
    async def login(
        response: Response, credentials: OAuth2PasswordRequestForm = Depends()
    ):
        user = await user_db.authenticate(credentials)

        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        elif not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return await auth.get_login_response(user, response)

    return router
