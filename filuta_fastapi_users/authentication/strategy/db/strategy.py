import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional

from filuta_fastapi_users import exceptions, models
from filuta_fastapi_users.authentication.strategy.base import Strategy
from filuta_fastapi_users.authentication.strategy.db.adapter import AccessTokenDatabase,RefreshTokenDatabase, OtpTokenDatabase
from filuta_fastapi_users.authentication.strategy.db.models import AP, OTPTP, RTP
from filuta_fastapi_users.manager import BaseUserManager

class DatabaseStrategy(
    Strategy[models.UP, models.ID], 
    Generic[models.UP, models.ID, AP]
):
    def __init__(
        self, 
        access_token_db: AccessTokenDatabase[AP],
        otp_token_db = OtpTokenDatabase[OTPTP],
        lifetime_seconds: Optional[int] = None
    ):
        self.access_token_db = access_token_db
        self.otp_token_db = otp_token_db
        self.lifetime_seconds = lifetime_seconds

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.lifetime_seconds
            )

        access_token = await self.access_token_db.get_by_token(token, max_age)
        if access_token is None:
            return None

        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def get_token_record(
        self, token: Optional[str]
    ) -> Optional[models.UP]:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.lifetime_seconds
            )

        access_token = await self.access_token_db.get_by_token(token, max_age)
        return access_token

    async def write_token(self, user: models.UP) -> str:
        access_token_dict = self._create_access_token_dict(user)
        access_token = await self.access_token_db.create(access_token_dict)
        return access_token

    async def update_token(self, access_token, data) -> str:
        access_token = await self.access_token_db.update(access_token=access_token, update_dict=data)
        return access_token

    async def destroy_token(self, token: str, user: models.UP) -> None:
        access_token = await self.access_token_db.get_by_token(token)
        if access_token is not None:
            await self.access_token_db.delete(access_token)

    def _create_access_token_dict(self, user: models.UP) -> Dict[str, Any]:
        token = secrets.token_urlsafe()
        return {"token": token, "user_id": user.id, "scopes": "none", "mfa_scopes": {"email": 0}}

    async def create_otp_email_token(self, access_token, mfa_token):
        otp_record = await self.otp_token_db.create({"access_token": access_token, "mfa_type": "email", "mfa_token": mfa_token})
        return otp_record

    async def find_otp_token(self, access_token, mfa_type, mfa_token):
        otp_record = await self.otp_token_db.find_otp_token(access_token=access_token, mfa_type=mfa_type, mfa_token=mfa_token)
        return otp_record