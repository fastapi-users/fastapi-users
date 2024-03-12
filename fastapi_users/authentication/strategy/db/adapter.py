from datetime import datetime
from typing import Any, Dict, Generic, Optional, Protocol, TypeVar

from fastapi_users.authentication.strategy.db.models import AP, APE

TokenIdentityType = TypeVar("TokenIdentityType", covariant=True)
TokenType = TypeVar("TokenType")


class BaseAccessTokenDatabase(Protocol, Generic[TokenIdentityType, TokenType]):
    """Protocol for retrieving, creating and updating access tokens from a database."""

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[TokenType]:
        """Get a single access token by token."""
        ...  # pragma: no cover

    async def create(self, create_dict: Dict[str, Any]) -> TokenType:
        """Create an access token."""
        ...  # pragma: no cover

    async def update(
        self, access_token: TokenType, update_dict: Dict[str, Any]
    ) -> TokenType:
        """Update an access token."""
        ...  # pragma: no cover

    async def delete(self, access_token: TokenType) -> None:
        """Delete an access token."""
        ...  # pragma: no cover


class AccessTokenDatabase(BaseAccessTokenDatabase[str, AP], Generic[AP]):
    """Protocol for retrieving, creating and updating access tokens from a database."""


class AccessRefreshTokenDatabase(BaseAccessTokenDatabase[str, APE], Generic[APE]):
    async def get_by_refresh_token(
        self, refresh_token: str, max_age: Optional[datetime] = None
    ) -> Optional[APE]:
        """Get a single access token by refresh token"""
        ...
