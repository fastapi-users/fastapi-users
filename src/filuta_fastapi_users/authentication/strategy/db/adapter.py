from datetime import datetime
from typing import Any, Generic, Protocol

from filuta_fastapi_users import models


class AccessTokenDatabase(Protocol, Generic[models.AP]):
    """Protocol for retrieving, creating and updating access tokens from a database."""

    async def get_by_token(
        self,
        token: str,
        max_age: datetime | None = None,
        authorized: bool = False,
        ignore_expired: bool = False,
    ) -> models.AP | None:
        """Get a single access token by token."""
        ...  # pragma: no cover

    async def create(self, create_dict: dict[str, Any]) -> models.AP:
        """Create an access token."""
        ...  # pragma: no cover

    async def update(self, access_token: models.AP, update_dict: dict[str, Any]) -> models.AP:
        """Update an access token."""
        ...  # pragma: no cover

    async def delete(self, access_token: models.AP) -> None:
        """Delete an access token."""
        ...  # pragma: no cover

    async def delete_all_records_for_user(self, user: models.UP) -> None:
        """Delete all tokens for a given user"""
        ...  # pragma: no cover

    async def get_latest_token_for_user(self, user: models.UP) -> models.AP:
        """Delete latest token for a user"""
        ...  # pragma: no cover


class RefreshTokenDatabase(Protocol, Generic[models.RTP]):
    """Protocol for retrieving, creating and updating refresh tokens from a database."""

    async def get_by_token(self, token: str, max_age: datetime | None = None) -> models.RTP | None:
        """Get a single refresh token by token."""
        ...  # pragma: no cover

    async def create(self, create_dict: dict[str, Any]) -> models.RTP:
        """Create an refresh token."""
        ...  # pragma: no cover

    async def update(self, refresh_token: models.RTP, update_dict: dict[str, Any]) -> models.RTP:
        """Update an refresh token."""
        ...  # pragma: no cover

    async def delete(self, refresh_token: models.RTP) -> None:
        """Delete an refresh token."""
        ...  # pragma: no cover

    async def delete_all_records_for_user(self, user: models.UP) -> None:
        """Delete all tokens for a given user"""
        ...  # pragma: no cover


class OtpTokenDatabase(Protocol, Generic[models.OTPTP]):
    """Protocol for retrieving, creating and updating OTP tokens from a database."""

    async def get_by_access_token(self, token: str, max_age: datetime | None = None) -> models.OTPTP | None:
        """Get a single OTP token by token."""
        ...  # pragma: no cover

    async def create(self, create_dict: dict[str, Any]) -> models.OTPTP:
        """Create an OTP token."""
        ...  # pragma: no cover

    async def update(self, otp_token: models.OTPTP, update_dict: dict[str, Any]) -> models.OTPTP:
        """Update an OTP token."""
        ...  # pragma: no cover

    async def delete(self, otp_record: models.OTPTP) -> None:
        """Delete an OTP token."""
        ...  # pragma: no cover

    async def find_otp_token(
        self, access_token: str, mfa_type: str, mfa_token: str, only_valid: bool = False
    ) -> models.OTPTP | None:
        """Finds an OTP token."""
        ...  # pragma: no cover

    async def user_has_token(self, access_token: str, mfa_type: str) -> models.OTPTP | None:
        """Checks whether an user has an OTP token"""
        ...  # pragma: no cover
