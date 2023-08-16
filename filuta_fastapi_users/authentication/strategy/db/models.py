from datetime import datetime
from typing import Protocol, TypeVar

from filuta_fastapi_users import models


class AccessTokenProtocol(Protocol[models.ID]):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: models.ID
    created_at: datetime


AP = TypeVar("AP", bound=AccessTokenProtocol)


class RefreshTokenProtocol(Protocol[models.ID]):
    """Refresh token protocol that ORM model should follow."""

    token: str
    user_id: models.ID
    created_at: datetime


RTP = TypeVar("RTP", bound=RefreshTokenProtocol)


class OtpTokenProtocol(Protocol[models.ID]):
    """OTP token protocol that ORM model should follow."""

    access_token: str
    mfa_type: str
    mfa_token: str
    created_at: datetime
    expire_at: datetime


OTPTP = TypeVar("OTPTP", bound=OtpTokenProtocol)
