from typing import Any, Generic, Optional, TypeVar

from fastapi import Response
from fastapi.security.base import SecurityBase

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB

T = TypeVar("T")


class BaseAuthentication(Generic[T]):
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
        self, credentials: Optional[T], user_db: BaseUserDatabase
    ) -> Optional[BaseUserDB]:
        raise NotImplementedError()

    async def get_login_response(self, user: BaseUserDB, response: Response) -> Any:
        raise NotImplementedError()

    async def get_logout_response(self, user: BaseUserDB, response: Response) -> Any:
        raise NotImplementedError()
