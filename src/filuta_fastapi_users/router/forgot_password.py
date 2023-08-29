from fastapi import APIRouter, Body, Depends, Request, status
from pydantic import EmailStr

from filuta_fastapi_users import exceptions, models
from filuta_fastapi_users.manager import BaseUserManager, UserManagerDependency


def get_forgot_password_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
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
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ) -> None:
        try:
            user = await user_manager.get_by_email(email)
        except exceptions.UserNotExists:
            return

        try:
            await user_manager.forgot_password(user, request)
        except exceptions.UserInactive:
            pass

    return router
