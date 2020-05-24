from typing import Any, Callable, Dict, Optional, Type, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import UUID4

from fastapi_users import models
from fastapi_users.authentication import Authenticator
from fastapi_users.db import BaseUserDatabase
from fastapi_users.password import get_password_hash
from fastapi_users.router.common import run_handler


def get_users_router(
    user_db: BaseUserDatabase[models.BaseUserDB],
    user_model: Type[models.BaseUser],
    user_update_model: Type[models.BaseUserUpdate],
    user_db_model: Type[models.BaseUserDB],
    authenticator: Authenticator,
    after_update: Optional[Callable[[models.UD, Dict[str, Any], Request], None]] = None,
) -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()

    get_current_active_user = authenticator.get_current_active_user
    get_current_superuser = authenticator.get_current_superuser

    async def _get_or_404(id: UUID4) -> models.BaseUserDB:
        user = await user_db.get(id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def _update_user(
        user: models.BaseUserDB, update_dict: Dict[str, Any], request: Request
    ):
        for field in update_dict:
            if field == "password":
                hashed_password = get_password_hash(update_dict[field])
                user.hashed_password = hashed_password
            else:
                setattr(user, field, update_dict[field])
        updated_user = await user_db.update(user)
        if after_update:
            await run_handler(after_update, updated_user, update_dict, request)
        return updated_user

    @router.get("/me", response_model=user_model)
    async def me(
        user: user_db_model = Depends(get_current_active_user),  # type: ignore
    ):
        return user

    @router.patch("/me", response_model=user_model)
    async def update_me(
        request: Request,
        updated_user: user_update_model,  # type: ignore
        user: user_db_model = Depends(get_current_active_user),  # type: ignore
    ):
        updated_user = cast(
            models.BaseUserUpdate, updated_user,
        )  # Prevent mypy complain
        updated_user_data = updated_user.create_update_dict()
        updated_user = await _update_user(user, updated_user_data, request)

        return updated_user

    @router.get(
        "/{id}",
        response_model=user_model,
        dependencies=[Depends(get_current_superuser)],
    )
    async def get_user(id: UUID4):
        return await _get_or_404(id)

    @router.patch(
        "/{id}",
        response_model=user_model,
        dependencies=[Depends(get_current_superuser)],
    )
    async def update_user(
        id: UUID4, updated_user: user_update_model, request: Request  # type: ignore
    ):
        updated_user = cast(
            models.BaseUserUpdate, updated_user,
        )  # Prevent mypy complain
        user = await _get_or_404(id)
        updated_user_data = updated_user.create_update_dict_superuser()
        return await _update_user(user, updated_user_data, request)

    @router.delete(
        "/{id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(get_current_superuser)],
    )
    async def delete_user(id: UUID4):
        user = await _get_or_404(id)
        await user_db.delete(user)
        return None

    return router
