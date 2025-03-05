from datetime import datetime
from typing import Generic, Protocol, TypeVar

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    """User protocol that ORM model should follow."""

    id: ID
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_poweruser: bool
    is_verified: bool


class OAuthAccountProtocol(Protocol[ID]):
    """OAuth account protocol that ORM model should follow."""

    id: ID
    oauth_name: str
    access_token: str
    expires_at: int | None
    refresh_token: str | None
    account_id: str
    account_email: str


UP = TypeVar("UP", bound=UserProtocol)  # type: ignore
OAP = TypeVar("OAP", bound=OAuthAccountProtocol)  # type: ignore


class UserOAuthProtocol(UserProtocol[ID], Generic[ID, OAP]):
    """User protocol including a list of OAuth accounts."""

    id: ID
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_poweruser: bool
    is_verified: bool
    oauth_accounts: list[OAP]


UOAP = TypeVar("UOAP", bound=UserOAuthProtocol)  # type: ignore


class AccessTokenProtocol(Protocol[ID]):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: ID
    created_at: datetime
    scopes: str
    mfa_scopes: dict[str, int]


AP = TypeVar("AP", bound=AccessTokenProtocol)  # type: ignore


class RefreshTokenProtocol(Protocol[ID]):
    """Refresh token protocol that ORM model should follow."""

    token: str
    user_id: ID
    created_at: datetime


RTP = TypeVar("RTP", bound=RefreshTokenProtocol)  # type: ignore


class OtpTokenProtocol(Protocol):
    """OTP token protocol that ORM model should follow."""

    access_token: str
    mfa_type: str
    mfa_token: str
    created_at: datetime
    expire_at: datetime


OTPTP = TypeVar("OTPTP", bound=OtpTokenProtocol)
