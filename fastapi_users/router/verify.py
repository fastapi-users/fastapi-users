from typing import Type

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr

from fastapi_users import models
from fastapi_users.manager import (
    BaseUserManager,
    InvalidVerifyToken,
    UserAlreadyVerified,
    UserInactive,
    UserManagerDependency,
    UserNotExists,
)
from fastapi_users.router.common import ErrorCode


def get_verify_router(
    get_user_manager: UserManagerDependency[models.UC, models.UD],
    user_model: Type[models.U],
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
            await user_manager.request_verify(user, request)
        except (UserNotExists, UserInactive, UserAlreadyVerified):
            pass

        return None

    @router.post("/verify", response_model=user_model)
    async def verify(
        request: Request,
        token: str = Body(..., embed=True),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        try:
            return await user_manager.verify(token, request)
        except (InvalidVerifyToken, UserNotExists):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )
        except UserAlreadyVerified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
            )

    return router
