from typing import Callable, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Request, status

from fastapi_users import models
from fastapi_users.manager import (
    InvalidPasswordException,
    UserAlreadyExists,
    UserManager,
    UserManagerDependency,
)
from fastapi_users.router.common import ErrorCode, run_handler


def get_register_router(
    get_user_manager: UserManagerDependency[models.UD],
    user_model: Type[models.U],
    user_create_model: Type[models.UC],
    after_register: Optional[Callable[[models.UD, Request], None]] = None,
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register", response_model=user_model, status_code=status.HTTP_201_CREATED
    )
    async def register(
        request: Request,
        user: user_create_model,  # type: ignore
        user_manager: UserManager[models.UD] = Depends(get_user_manager),
    ):
        try:
            created_user = await user_manager.create(user, safe=True)
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

        if after_register:
            await run_handler(after_register, created_user, request)

        return created_user

    return router
