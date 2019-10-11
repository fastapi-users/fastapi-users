from typing import Callable

from fastapi import HTTPException
from starlette import status
from starlette.responses import Response

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB

credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


class BaseAuthentication:
    """
    Base adapter for generating and decoding authentication tokens.

    Provides dependency injectors to get current active/superuser user.
    """

    async def get_login_response(self, user: BaseUserDB, response: Response):
        raise NotImplementedError()

    def get_current_user(self, user_db: BaseUserDatabase):
        raise NotImplementedError()

    def get_current_active_user(self, user_db: BaseUserDatabase):
        raise NotImplementedError()

    def get_current_superuser(self, user_db: BaseUserDatabase):
        raise NotImplementedError()

    def _get_authentication_method(
        self, user_db: BaseUserDatabase
    ) -> Callable[..., BaseUserDB]:
        raise NotImplementedError()

    def _get_current_user_base(self, user: BaseUserDB) -> BaseUserDB:
        if user is None:
            raise self._get_credentials_exception()
        return user

    def _get_current_active_user_base(self, user: BaseUserDB) -> BaseUserDB:
        user = self._get_current_user_base(user)
        if not user.is_active:
            raise self._get_credentials_exception()
        return user

    def _get_current_superuser_base(self, user: BaseUserDB) -> BaseUserDB:
        user = self._get_current_active_user_base(user)
        if not user.is_superuser:
            raise self._get_credentials_exception(status.HTTP_403_FORBIDDEN)
        return user

    def _get_credentials_exception(
        self, status_code: int = status.HTTP_401_UNAUTHORIZED
    ) -> HTTPException:
        return HTTPException(status_code=status_code)
