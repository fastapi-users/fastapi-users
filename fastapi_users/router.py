import asyncio
import typing
from collections import defaultdict
from enum import Enum, auto

import jwt
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from starlette import status
from starlette.responses import Response

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUser, Models
from fastapi_users.password import get_password_hash
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt


class ErrorCode:
    REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    RESET_PASSWORD_BAD_TOKEN = "RESET_PASSWORD_BAD_TOKEN"


class Event(Enum):
    ON_AFTER_REGISTER = auto()
    ON_AFTER_FORGOT_PASSWORD = auto()


class UserRouter(APIRouter):
    event_handlers: typing.DefaultDict[Event, typing.List[typing.Callable]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_handlers = defaultdict(list)

    def add_event_handler(self, event_type: Event, func: typing.Callable) -> None:
        self.event_handlers[event_type].append(func)

    async def run_handlers(self, event_type: Event, *args, **kwargs) -> None:
        for handler in self.event_handlers[event_type]:
            if asyncio.iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            else:
                handler(*args, **kwargs)


def get_user_router(
    user_db: BaseUserDatabase,
    user_model: typing.Type[BaseUser],
    auth: BaseAuthentication,
    reset_password_token_secret: str,
    reset_password_token_lifetime_seconds: int = 3600,
) -> UserRouter:
    """Generate a router with the authentication routes."""
    router = UserRouter()
    models = Models(user_model)

    reset_password_token_audience = "fastapi-users:reset"

    get_current_active_user = auth.get_current_active_user(user_db)
    get_current_superuser = auth.get_current_superuser(user_db)

    async def _get_or_404(id: str) -> models.UserDB:  # type: ignore
        user = await user_db.get(id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def _update_user(
        user: models.UserDB, update_dict: typing.Dict[str, typing.Any]  # type: ignore
    ):
        for field in update_dict:
            if field == "password":
                hashed_password = get_password_hash(update_dict[field])
                user.hashed_password = hashed_password
            else:
                setattr(user, field, update_dict[field])
        return await user_db.update(user)

    @router.post(
        "/register", response_model=models.User, status_code=status.HTTP_201_CREATED
    )
    async def register(user: models.UserCreate):  # type: ignore
        existing_user = await user_db.get_by_email(user.email)

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )

        hashed_password = get_password_hash(user.password)
        db_user = models.UserDB(
            **user.create_update_dict(), hashed_password=hashed_password
        )
        created_user = await user_db.create(db_user)

        await router.run_handlers(Event.ON_AFTER_REGISTER, created_user)

        return created_user

    @router.post("/login")
    async def login(
        response: Response, credentials: OAuth2PasswordRequestForm = Depends()
    ):
        user = await user_db.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )

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
            await router.run_handlers(Event.ON_AFTER_FORGOT_PASSWORD, user, token)

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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )

            user = await user_db.get(user_id)
            if user is None or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )

            user.hashed_password = get_password_hash(password)
            await user_db.update(user)
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )

    @router.get("/me", response_model=models.User)
    async def me(
        user: models.UserDB = Depends(get_current_active_user),  # type: ignore
    ):
        return user

    @router.patch("/me", response_model=models.User)
    async def update_me(
        updated_user: models.UserUpdate,  # type: ignore
        user: models.UserDB = Depends(get_current_active_user),  # type: ignore
    ):
        updated_user_data = updated_user.create_update_dict()
        return await _update_user(user, updated_user_data)

    @router.get("/", response_model=typing.List[models.User])  # type: ignore
    async def list_users(
        superuser: models.UserDB = Depends(get_current_superuser),  # type: ignore
    ):
        return await user_db.list()

    @router.get("/{id}", response_model=models.User)
    async def get_user(
        id: str,
        superuser: models.UserDB = Depends(get_current_superuser),  # type: ignore
    ):
        return await _get_or_404(id)

    @router.patch("/{id}", response_model=models.User)
    async def update_user(
        id: str,
        updated_user: models.UserUpdate,  # type: ignore
        superuser: models.UserDB = Depends(get_current_superuser),  # type: ignore
    ):
        user = await _get_or_404(id)
        updated_user_data = updated_user.create_update_dict_superuser()
        return await _update_user(user, updated_user_data)

    @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_user(
        id: str,
        superuser: models.UserDB = Depends(get_current_superuser),  # type: ignore
    ):
        user = await _get_or_404(id)
        await user_db.delete(user)
        return None

    return router
