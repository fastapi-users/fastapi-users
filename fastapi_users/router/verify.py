from typing import Callable, Optional, Type

import jwt
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import UUID4, EmailStr

from fastapi_users import models
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.manager import (
    BaseUserManager,
    UserAlreadyVerified,
    UserManagerDependency,
    UserNotExists,
)
from fastapi_users.router.common import ErrorCode, run_handler

VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"


def get_verify_router(
    get_user_manager: UserManagerDependency[models.UC, models.UD],
    user_model: Type[models.U],
    verification_token_secret: SecretType,
    verification_token_lifetime_seconds: int = 3600,
    after_verification_request: Optional[
        Callable[[models.UD, str, Request], None]
    ] = None,
    after_verification: Optional[Callable[[models.UD, Request], None]] = None,
):
    router = APIRouter()

    @router.post("/request-verify-token", status_code=status.HTTP_202_ACCEPTED)
    async def request_verify_token(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.get_by_email(email)
            if not user.is_verified and user.is_active:
                token_data = {
                    "user_id": str(user.id),
                    "email": email,
                    "aud": VERIFY_USER_TOKEN_AUDIENCE,
                }
                token = generate_jwt(
                    token_data,
                    verification_token_secret,
                    verification_token_lifetime_seconds,
                )

                if after_verification_request:
                    await run_handler(after_verification_request, user, token, request)
        except UserNotExists:
            pass

        return None

    @router.post("/verify", response_model=user_model)
    async def verify(
        request: Request,
        token: str = Body(..., embed=True),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        try:
            data = decode_jwt(
                token, verification_token_secret, [VERIFY_USER_TOKEN_AUDIENCE]
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_TOKEN_EXPIRED,
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        try:
            user_id = data["user_id"]
            email = data["email"]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        try:
            user_check = await user_manager.get_by_email(email)
        except UserNotExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        try:
            user_uuid = UUID4(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        if user_check.id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        try:
            user = await user_manager.verify(user_check)
        except UserAlreadyVerified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
            )

        if after_verification:
            await run_handler(after_verification, user, request)

        return user

    return router
