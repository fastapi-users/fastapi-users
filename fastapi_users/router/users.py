from typing import Any, Callable, Dict, Optional, Type, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from pydantic import UUID4

from fastapi_users import models
from fastapi_users.authentication import Authenticator
from fastapi_users.db import BaseUserDatabase
from fastapi_users.password import get_password_hash
from fastapi_users.router.common import ErrorCode, run_handler
from fastapi_users.user import InvalidPasswordException, ValidatePasswordProtocol


def get_users_router(
    user_db: BaseUserDatabase[models.BaseUserDB],
    user_model: Type[models.BaseUser],
    user_update_model: Type[models.BaseUserUpdate],
    user_db_model: Type[models.BaseUserDB],
    authenticator: Authenticator,
    after_update: Optional[Callable[[models.UD, Dict[str, Any], Request], None]] = None,
    requires_verification: bool = False,
    validate_password: Optional[ValidatePasswordProtocol] = None,
) -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()

    get_current_active_user = authenticator.current_user(
        active=True, verified=requires_verification
    )
    get_current_superuser = authenticator.current_user(
        active=True, verified=requires_verification, superuser=True
    )

    async def _get_or_404(id: UUID4) -> models.BaseUserDB:
        user = await user_db.get(id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def _check_unique_email(
        updated_user: user_update_model,  # type: ignore
    ) -> None:
        updated_user = cast(
            models.BaseUserUpdate, updated_user
        )  # Prevent mypy complain
        if updated_user.email:
            user = await user_db.get_by_email(updated_user.email)
            if user is not None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
                )

    async def _update_user(
        user: models.BaseUserDB, update_dict: Dict[str, Any], request: Request
    ):
        for field in update_dict:
            if field == "password":
                password = update_dict[field]
                if validate_password:
                    await validate_password(password, user)
                hashed_password = get_password_hash(password)
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

    @router.patch(
        "/me",
        response_model=user_model,
        dependencies=[Depends(get_current_active_user), Depends(_check_unique_email)],
    )
    async def update_me(
        request: Request,
        updated_user: user_update_model,  # type: ignore
        user: user_db_model = Depends(get_current_active_user),  # type: ignore
    ):
        updated_user = cast(
            models.BaseUserUpdate,
            updated_user,
        )  # Prevent mypy complain
        updated_user_data = updated_user.create_update_dict()

        try:
            return await _update_user(user, updated_user_data, request)
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    @router.get(
        "/{id:uuid}",
        response_model=user_model,
        dependencies=[Depends(get_current_superuser)],
    )
    async def get_user(id: UUID4):
        return await _get_or_404(id)

    @router.patch(
        "/{id:uuid}",
        response_model=user_model,
        dependencies=[Depends(get_current_superuser), Depends(_check_unique_email)],
    )
    async def update_user(
        id: UUID4, updated_user: user_update_model, request: Request  # type: ignore
    ):
        updated_user = cast(
            models.BaseUserUpdate,
            updated_user,
        )  # Prevent mypy complain
        user = await _get_or_404(id)
        updated_user_data = updated_user.create_update_dict_superuser()

        try:
            return await _update_user(user, updated_user_data, request)
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    @router.delete(
        "/{id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        dependencies=[Depends(get_current_superuser)],
    )
    async def delete_user(id: UUID4):
        user = await _get_or_404(id)
        await user_db.delete(user)
        return None

    return router
