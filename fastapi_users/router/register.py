from typing import Callable, Optional, Type

from fastapi import APIRouter, HTTPException, Request, status

from fastapi_users import models
from fastapi_users.router.common import ErrorCode, run_handler
from fastapi_users.user import CreateUserProtocol, UserAlreadyExists


def get_register_router(
    create_user: CreateUserProtocol,
    user_model: Type[models.BaseUser],
    user_create_model: Type[models.BaseUserCreate],
    after_register: Optional[Callable[[models.UD, Request], None]] = None,
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register", response_model=user_model, status_code=status.HTTP_201_CREATED
    )
    async def register(request: Request, user: user_create_model):  # type: ignore
        try:
            created_user = await create_user(user, safe=True)
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )

        if after_register:
            await run_handler(after_register, created_user, request)

        return created_user

    return router
