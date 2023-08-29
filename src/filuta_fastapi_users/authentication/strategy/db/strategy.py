import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, Generic

from filuta_fastapi_users import exceptions, models
from filuta_fastapi_users.authentication.strategy.base import Strategy
from filuta_fastapi_users.authentication.strategy.db.adapter import AccessTokenDatabase
from filuta_fastapi_users.manager import BaseUserManager


class DatabaseStrategy(Strategy[models.UP, models.ID, models.AP], Generic[models.UP, models.ID, models.AP]):
    def __init__(self, access_token_db: AccessTokenDatabase[models.AP], lifetime_seconds: int | None = None):
        self.access_token_db = access_token_db
        self.lifetime_seconds = lifetime_seconds

    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models.UP, models.ID],
        authorized: bool = False,
        ignore_expired: bool = False,
    ) -> models.UP | None:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds is not None:
            max_age = datetime.now(UTC) - timedelta(seconds=self.lifetime_seconds)

        access_token = await self.access_token_db.get_by_token(token, max_age, authorized, ignore_expired)
        if access_token is None:
            return None

        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def get_token_record(self, token: str | None) -> models.AP | None:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds is not None:
            max_age = datetime.now(UTC) - timedelta(seconds=self.lifetime_seconds)

        access_token = await self.access_token_db.get_by_token(token, max_age)
        return access_token

    async def get_token_record_raw(self, token: str | None) -> models.AP | None:
        if token is None:
            return None

        access_token = await self.access_token_db.get_by_token(token)
        return access_token

    async def write_token(self, user: models.UP) -> models.AP:
        access_token_dict = self._create_access_token_dict(user)
        access_token = await self.access_token_db.create(access_token_dict)
        return access_token

    async def insert_token(self, access_token_dict: dict[str, Any]) -> models.AP:
        access_token = await self.access_token_db.create(access_token_dict)
        return access_token

    async def update_token(self, access_token: models.AP, data: dict[str, Any]) -> models.AP:
        access_token = await self.access_token_db.update(access_token, data)
        return access_token

    async def destroy_token(self, token: str) -> None:
        access_token = await self.access_token_db.get_by_token(token)
        if access_token is not None:
            await self.access_token_db.delete(access_token)

    def _create_access_token_dict(self, user: models.UP) -> dict[str, Any]:
        token = self.generate_token()
        return {"token": token, "user_id": user.id, "scopes": "none", "mfa_scopes": {"email": 0}}

    def generate_token(self) -> str:
        return secrets.token_urlsafe()
