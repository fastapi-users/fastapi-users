from typing import Type

from fastapi import APIRouter, Depends, HTTPException, Request, status

from fastapi_users import models
from fastapi_users.manager import (
    BaseUserManager,
    InvalidPasswordException,
    UserAlreadyExists,
    UserManagerDependency,
)
from fastapi_users.router.common import ErrorCode, ErrorModel


def get_register_router(
    get_user_manager: UserManagerDependency[models.UC, models.UD],
    user_model: Type[models.U],
    user_create_model: Type[models.UC],
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register",
        response_model=user_model,
        status_code=status.HTTP_201_CREATED,
        name="register:register",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.REGISTER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def register(
        request: Request,
        user: user_create_model,  # type: ignore
        user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
    ):
        try:
            created_user = await user_manager.create(user, safe=True, request=request)
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

        return created_user

    return router
