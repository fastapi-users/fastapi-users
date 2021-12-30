import secrets
from datetime import datetime, timedelta, timezone
from typing import Generic, Optional

from fastapi_users import models
from fastapi_users.authentication.strategy.base import Strategy
from fastapi_users.authentication.strategy.db.adapter import AccessTokenDatabase
from fastapi_users.authentication.strategy.db.models import A
from fastapi_users.manager import BaseUserManager, UserNotExists


class DatabaseStrategy(Strategy, Generic[models.UC, models.UD, A]):
    def __init__(
        self, database: AccessTokenDatabase[A], lifetime_seconds: Optional[int] = None
    ):
        self.database = database
        self.lifetime_seconds = lifetime_seconds

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UC, models.UD]
    ) -> Optional[models.UD]:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.lifetime_seconds
            )

        access_token = await self.database.get_by_token(token, max_age)
        if access_token is None:
            return None

        try:
            user_id = access_token.user_id
            return await user_manager.get(user_id)
        except UserNotExists:
            return None

    async def write_token(self, user: models.UD) -> str:
        access_token = self._create_access_token(user)
        await self.database.create(access_token)
        return access_token.token

    async def destroy_token(self, token: str, user: models.UD) -> None:
        access_token = await self.database.get_by_token(token)
        if access_token is not None:
            await self.database.delete(access_token)

    def _create_access_token(self, user: models.UD) -> A:
        token = secrets.token_urlsafe()
        return self.database.access_token_model(token=token, user_id=user.id)
