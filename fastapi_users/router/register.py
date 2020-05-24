from typing import Callable, Optional, Type, cast

from fastapi import APIRouter, HTTPException, Request, status

from fastapi_users import models
from fastapi_users.db import BaseUserDatabase
from fastapi_users.password import get_password_hash
from fastapi_users.router.common import ErrorCode, run_handler


def get_register_router(
    user_db: BaseUserDatabase[models.BaseUserDB],
    user_model: Type[models.BaseUser],
    user_create_model: Type[models.BaseUserCreate],
    user_db_model: Type[models.BaseUserDB],
    after_register: Optional[Callable[[models.UD, Request], None]] = None,
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register", response_model=user_model, status_code=status.HTTP_201_CREATED
    )
    async def register(request: Request, user: user_create_model):  # type: ignore
        user = cast(models.BaseUserCreate, user)  # Prevent mypy complain
        existing_user = await user_db.get_by_email(user.email)

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )

        hashed_password = get_password_hash(user.password)
        db_user = user_db_model(
            **user.create_update_dict(), hashed_password=hashed_password
        )
        created_user = await user_db.create(db_user)

        if after_register:
            await run_handler(after_register, created_user, request)

        return created_user

    return router
