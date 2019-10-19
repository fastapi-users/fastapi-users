import asyncio
from typing import Any, Callable, Type

import jwt
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.types import EmailStr
from starlette import status
from starlette.responses import Response

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUser, BaseUserDB, Models
from fastapi_users.password import get_password_hash
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt


def get_user_router(
    user_db: BaseUserDatabase,
    user_model: Type[BaseUser],
    auth: BaseAuthentication,
    on_after_forgot_password: Callable[[BaseUserDB, str], Any],
    reset_password_token_secret: str,
    reset_password_token_lifetime_seconds: int = 3600,
) -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()
    models = Models(user_model)

    reset_password_token_audience = "fastapi-users:reset"
    is_on_after_forgot_password_async = asyncio.iscoroutinefunction(
        on_after_forgot_password
    )

    @router.post(
        "/register", response_model=models.User, status_code=status.HTTP_201_CREATED
    )
    async def register(user: models.UserCreate):  # type: ignore
        existing_user = await user_db.get_by_email(user.email)

        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

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

    @router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
    async def forgot_password(email: EmailStr = Body(..., embed=True)):
        user = await user_db.get_by_email(email)

        if user is not None and user.is_active:
            token_data = {"user_id": user.id, "aud": reset_password_token_audience}
            token = generate_jwt(
                token_data,
                reset_password_token_lifetime_seconds,
                reset_password_token_secret,
            )
            if is_on_after_forgot_password_async:
                await on_after_forgot_password(user, token)
            else:
                on_after_forgot_password(user, token)

        return None

    @router.post("/reset-password")
    async def reset_password(token: str = Body(...), password: str = Body(...)):
        try:
            data = jwt.decode(
                token,
                reset_password_token_secret,
                audience=reset_password_token_audience,
                algorithms=[JWT_ALGORITHM],
            )
            user_id = data.get("user_id")
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            user = await user_db.get(user_id)
            if user is None or not user.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            user.hashed_password = get_password_hash(password)
            await user_db.update(user)
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return router
