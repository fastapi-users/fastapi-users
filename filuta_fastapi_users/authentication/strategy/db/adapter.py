from datetime import datetime
from typing import Any, Dict, Generic, Optional, Protocol

from filuta_fastapi_users.authentication.strategy.db.models import AP


class AccessTokenDatabase(Protocol, Generic[AP]):
    """Protocol for retrieving, creating and updating access tokens from a database."""

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[AP]:
        """Get a single access token by token."""
        ...  # pragma: no cover

    async def create(self, create_dict: Dict[str, Any]) -> AP:
        """Create an access token."""
        ...  # pragma: no cover

    async def update(self, access_token: AP, update_dict: Dict[str, Any]) -> AP:
        """Update an access token."""
        ...  # pragma: no cover

    async def delete(self, access_token: AP) -> None:
        """Delete an access token."""
        ...  # pragma: no cover


class RefreshTokenDatabase(Protocol, Generic[AP]):
    """Protocol for retrieving, creating and updating refresh tokens from a database."""

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[AP]:
        """Get a single refresh token by token."""
        ...  # pragma: no cover

    async def create(self, create_dict: Dict[str, Any]) -> AP:
        """Create an refresh token."""
        ...  # pragma: no cover

    async def update(self, refresh_token: AP, update_dict: Dict[str, Any]) -> AP:
        """Update an refresh token."""
        ...  # pragma: no cover

    async def delete(self, refresh_token: AP) -> None:
        """Delete an refresh token."""
        ...  # pragma: no cover

class OtpTokenDatabase(Protocol, Generic[AP]):
    """Protocol for retrieving, creating and updating OTP tokens from a database."""

    async def get_by_access_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[AP]:
        """Get a single OTP token by token."""
        ...  # pragma: no cover

    async def create(self, create_dict: Dict[str, Any]) -> AP:
        """Create an OTP token."""
        ...  # pragma: no cover

    async def update(self, refresh_token: AP, update_dict: Dict[str, Any]) -> AP:
        """Update an OTP token."""
        ...  # pragma: no cover

    async def delete(self, refresh_token: AP) -> None:
        """Delete an OTP token."""
        ...  # pragma: no cover
