import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional

from fastapi_users import exceptions, models
from fastapi_users.authentication.models import AccessRefreshToken
from fastapi_users.authentication.strategy.base import Strategy, StrategyRefresh
from fastapi_users.authentication.strategy.db.adapter import (
    AccessRefreshTokenDatabase,
    AccessTokenDatabase,
)
from fastapi_users.authentication.strategy.db.models import AP, APE
from fastapi_users.manager import BaseUserManager


class DatabaseStrategy(
    Strategy[models.UP, models.ID], Generic[models.UP, models.ID, AP]
):
    def __init__(
        self, database: AccessTokenDatabase[AP], lifetime_seconds: Optional[int] = None
    ):
        self.database = database
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

        access_token = await self.database.get_by_token(token, max_age)
        if access_token is None:
            return None

        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: models.UP) -> str:
        access_token_dict = self._create_access_token_dict(user)
        access_token = await self.database.create(access_token_dict)
        return access_token.token

    async def destroy_token(self, token: str, user: models.UP) -> None:
        access_token = await self.database.get_by_token(token)
        if access_token is not None:
            await self.database.delete(access_token)

    def _create_access_token_dict(self, user: models.UP) -> Dict[str, Any]:
        token = secrets.token_urlsafe()
        return {"token": token, "user_id": user.id}


class DatabaseRefreshStrategy(
    DatabaseStrategy[models.UP, models.ID, APE],
    StrategyRefresh[models.UP, models.ID],
    Generic[models.UP, models.ID, APE],
):
    database: AccessRefreshTokenDatabase[APE]
    refresh_lifetime_seconds: Optional[int]

    def __init__(
        self,
        database: AccessRefreshTokenDatabase[APE],
        lifetime_seconds: Optional[int] = None,
        refresh_lifetime_seconds: Optional[int] = None,
    ):
        super().__init__(database, lifetime_seconds)
        self.refresh_lifetime_seconds = refresh_lifetime_seconds

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
        refresh_token: Optional[str] = None,
    ) -> Optional[models.UP]:
        if token is not None:
            return await super().read_token(token, user_manager)
        if refresh_token is None:
            return None
        max_age = None
        if self.refresh_lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.refresh_lifetime_seconds
            )
        access_token = await self.database.get_by_refresh_token(
            refresh_token=refresh_token, max_age=max_age
        )
        if access_token is None:
            return None
        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: models.UP) -> AccessRefreshToken:
        access_token_dict = self._create_access_token_dict(user)
        token = await self.database.create(access_token_dict)
        return (token.token, token.refresh_token)

    async def destroy_token(
        self,
        token: Optional[str],
        user: models.UP,
        refresh_token: Optional[str] = None,
    ) -> None:
        if token is not None:
            return await super().destroy_token(token, user)
        if refresh_token is not None:
            access_token = await self.database.get_by_refresh_token(
                refresh_token=refresh_token
            )
            if access_token is not None:
                await self.database.delete(access_token)

    def _create_access_token_dict(self, user: models.UP) -> Dict[str, Any]:
        token_dict = super()._create_access_token_dict(user)
        refresh_token = secrets.token_urlsafe()
        token_dict["refresh_token"] = refresh_token
        return token_dict
