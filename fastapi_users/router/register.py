from typing import Callable, Optional, Type, cast

import jwt
from fastapi import APIRouter, Body, HTTPException, Request, status
from pydantic import UUID4

from fastapi_users import models
from fastapi_users.router.common import ErrorCode, run_handler
from fastapi_users.user import (
    ActivateUserProtocol,
    CreateUserProtocol,
    UserAlreadyActivated,
    UserAlreadyExists,
    UserNotExists,
)
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt

ACTIVATE_USER_TOKEN_AUDIENCE = "fastapi-users:activate"


def get_register_router(
    create_user: CreateUserProtocol,
    user_model: Type[models.BaseUser],
    user_create_model: Type[models.BaseUserCreate],
    after_register: Optional[Callable[[models.UD, Request], None]] = None,
    activation_callback: Optional[Callable[[models.UD, str, Request], None]] = None,
    activate_user: ActivateUserProtocol = None,
    activation_token_secret: str = None,
    activation_token_lifetime_seconds: int = 3600,
) -> APIRouter:
    """Generate a router with the register route."""

    if activation_callback and not activation_token_secret:
        raise ValueError("Must supply activation_token_secret with activation_callback")
    if activation_callback and not activate_user:
        raise ValueError(
            "Must supply activate_user, the ActivateUserProtocol, with activation_callback"
        )

    router = APIRouter()

    @router.post(
        "/register", response_model=user_model, status_code=status.HTTP_201_CREATED
    )
    async def register(request: Request, user: user_create_model):  # type: ignore
        try:
            created_user = await create_user(
                user, safe=True, is_active=activation_callback is None
            )
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )

        if activation_callback:
            token_data = {
                "user_id": str(created_user.id),
                "aud": ACTIVATE_USER_TOKEN_AUDIENCE,
            }
            token = generate_jwt(
                token_data,
                activation_token_lifetime_seconds,
                activation_token_secret,
            )
            await run_handler(activation_callback, created_user, token, request)
        elif after_register:
            await run_handler(after_register, created_user, request)

        return created_user

    if activation_callback:

        @router.post(
            "/activate", response_model=user_model, status_code=status.HTTP_202_ACCEPTED
        )
        async def activate(request: Request, token: str = Body(...)):
            try:
                data = jwt.decode(
                    token,
                    activation_token_secret,
                    audience=ACTIVATE_USER_TOKEN_AUDIENCE,
                    algorithms=[JWT_ALGORITHM],
                )
            except jwt.exceptions.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.ACTIVATE_USER_TOKEN_EXPIRED,
                )
            except jwt.PyJWTError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.ACTIVATE_USER_BAD_TOKEN,
                )

            user_id = data.get("user_id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.ACTIVATE_USER_BAD_TOKEN,
                )

            try:
                user_uuid = UUID4(user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.ACTIVATE_USER_BAD_TOKEN,
                )

            try:
                user = await activate_user(user_uuid)
            except UserNotExists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.ACTIVATE_USER_BAD_TOKEN,
                )
            except UserAlreadyActivated:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.ACTIVATE_USER_LINK_USED,
                )
            if after_register:
                await run_handler(after_register, user, request)
            return user

    return router
