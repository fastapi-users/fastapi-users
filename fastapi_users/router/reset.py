from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr

from fastapi_users import models
from fastapi_users.manager import (
    BaseUserManager,
    InvalidPasswordException,
    InvalidResetPasswordToken,
    UserInactive,
    UserManagerDependency,
    UserNotExists,
)
from fastapi_users.router.common import ErrorCode, ErrorModel

RESET_PASSWORD_RESPONSES: Dict[int, Dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.RESET_PASSWORD_BAD_TOKEN: {
                        "summary": "Bad or expired token.",
                        "value": {"detail": ErrorCode.RESET_PASSWORD_BAD_TOKEN},
                    },
                    ErrorCode.RESET_PASSWORD_INVALID_PASSWORD: {
                        "summary": "Password validation failed.",
                        "value": {
                            "detail": {
                                "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                                "reason": "Password should be at least 3 characters",
                            }
                        },
                    },
                }
            }
        },
    },
}


def get_reset_password_router(
    get_user_manager: UserManagerDependency[models.UC, models.UD]
) -> APIRouter:
    """Generate a router with the reset password routes."""
    router = APIRouter()

    @router.post(
        "/forgot-password",
        status_code=status.HTTP_202_ACCEPTED,
        name="reset:forgot_password",
    )
    async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.get_by_email(email)
        except UserNotExists:
            return None

        try:
            await user_manager.forgot_password(user, request)
        except UserInactive:
            pass

        return None

    @router.post(
        "/reset-password",
        name="reset:reset_password",
        responses=RESET_PASSWORD_RESPONSES,
    )
    async def reset_password(
        request: Request,
        token: str = Body(...),
        password: str = Body(...),
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        try:
            await user_manager.reset_password(token, password, request)
        except (InvalidResetPasswordToken, UserNotExists, UserInactive):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    return router
