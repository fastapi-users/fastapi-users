from typing import Callable, Optional

import jwt
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import UUID4, EmailStr

from fastapi_users import models
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.manager import (
    BaseUserManager,
    InvalidPasswordException,
    UserManagerDependency,
    UserNotExists,
)
from fastapi_users.password import get_password_hash
from fastapi_users.router.common import ErrorCode, run_handler

RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"


def get_reset_password_router(
    get_user_manager: UserManagerDependency[models.UC, models.UD],
    reset_password_token_secret: SecretType,
    reset_password_token_lifetime_seconds: int = 3600,
    after_forgot_password: Optional[Callable[[models.UD, str, Request], None]] = None,
    after_reset_password: Optional[Callable[[models.UD, Request], None]] = None,
) -> APIRouter:
    """Generate a router with the reset password routes."""
    router = APIRouter()

    @router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
    async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.get_by_email(email)
        except UserNotExists:
            return None

        if user.is_active:
            token_data = {"user_id": str(user.id), "aud": RESET_PASSWORD_TOKEN_AUDIENCE}
            token = generate_jwt(
                token_data,
                reset_password_token_secret,
                reset_password_token_lifetime_seconds,
            )
            if after_forgot_password:
                await run_handler(after_forgot_password, user, token, request)

        return None

    @router.post("/reset-password")
    async def reset_password(
        request: Request,
        token: str = Body(...),
        password: str = Body(...),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        try:
            data = decode_jwt(
                token, reset_password_token_secret, [RESET_PASSWORD_TOKEN_AUDIENCE]
            )
            user_id = data.get("user_id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )

            try:
                user_uiid = UUID4(user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )

            try:
                user = await user_manager.get(user_uiid)
            except UserNotExists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )

            try:
                await user_manager.validate_password(password, user)
            except InvalidPasswordException as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                        "reason": e.reason,
                    },
                )

            user.hashed_password = get_password_hash(password)
            await user_manager.user_db.update(user)
            if after_reset_password:
                await run_handler(after_reset_password, user, request)
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )

    return router
