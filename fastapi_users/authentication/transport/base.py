from abc import abstractmethod
from typing import Generic, Protocol, TypeVar

from fastapi import Response
from fastapi.security.base import SecurityBase

from fastapi_users.authentication.models import AccessRefreshToken
from fastapi_users.openapi import OpenAPIResponseType

TokenType = TypeVar("TokenType", contravariant=True)


class TransportLogoutNotSupportedError(Exception):
    pass


class BaseTransport(Protocol, Generic[TokenType]):
    scheme: SecurityBase

    async def get_login_response(
        self, token: TokenType
    ) -> Response: ...  # pragma: no cover

    async def get_logout_response(self) -> Response: ...  # pragma: no cover

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        """Return a dictionary to use for the openapi responses route parameter."""
        ...  # pragma: no cover

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        """Return a dictionary to use for the openapi responses route parameter."""
        ...  # pragma: no cover


class Transport(BaseTransport[str]):
    pass


class TransportRefresh(BaseTransport[AccessRefreshToken]):
    @staticmethod
    @abstractmethod
    def get_openapi_refresh_responses_success() -> OpenAPIResponseType:
        """Return a dictionary to use for the openapi responses route parameter."""
        ...  # pragma: no cover
