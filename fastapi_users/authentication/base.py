from typing import Any, Dict, Generic, Optional, TypeVar

from fastapi import Response
from fastapi.security.base import SecurityBase

from fastapi_users import models
from fastapi_users.manager import BaseUserManager

T = TypeVar("T")


class BaseAuthentication(Generic[T, models.UC, models.UD]):
    """
    Base authentication backend.

    Every backend should derive from this class.

    :param name: Name of the backend.
    :param logout: Whether or not this backend has a logout process.
    """

    scheme: SecurityBase
    name: str
    logout: bool

    def __init__(self, name: str = "base", logout: bool = False):
        self.name = name
        self.logout = logout

    async def __call__(
        self,
        credentials: Optional[T],
        user_manager: BaseUserManager[models.UC, models.UD],
    ) -> Optional[models.UD]:
        raise NotImplementedError()

    async def get_login_response(
        self,
        user: models.UD,
        response: Response,
        user_manager: BaseUserManager[models.UC, models.UD],
    ) -> Any:
        raise NotImplementedError()

    @staticmethod
    def get_openapi_login_responses_success() -> Dict[str, Any]:
        """Return a dictionary to use for the openapi responses route parameter."""
        raise NotImplementedError()

    async def get_logout_response(
        self,
        user: models.UD,
        response: Response,
        user_manager: BaseUserManager[models.UC, models.UD],
    ) -> Any:
        raise NotImplementedError()

    @staticmethod
    def get_openapi_logout_responses_success() -> Dict[str, Any]:
        """Return a dictionary to use for the openapi responses route parameter."""
        raise NotImplementedError()
