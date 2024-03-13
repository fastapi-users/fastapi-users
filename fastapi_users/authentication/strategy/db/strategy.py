import secrets
from abc import abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional

from fastapi_users import exceptions, models
from fastapi_users.authentication.models import AccessRefreshToken, TokenType
from fastapi_users.authentication.strategy.base import (
    BaseStrategy,
    Strategy,
    StrategyRefresh,
)
from fastapi_users.authentication.strategy.db.adapter import (
    AccessRefreshTokenDatabase,
    BaseAccessTokenDatabase,
)
from fastapi_users.authentication.strategy.db.models import AP, APE
from fastapi_users.manager import BaseUserManager


class BaseDatabaseStrategy(
    BaseStrategy[models.UP, models.ID, str, TokenType],
    Generic[models.UP, models.ID, TokenType, AP],
):
    lifetime_seconds: Optional[int]
    database: BaseAccessTokenDatabase[str, AP]

    def __init__(
        self,
        database: BaseAccessTokenDatabase[str, AP],
        lifetime_seconds: Optional[int] = None,
    ):
        self.database = database
        self.lifetime_seconds = lifetime_seconds

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        access_token = await self._get_token(token)
        if access_token is None:
            return None
        return await self._get_user_by_id(access_token.user_id, user_manager)

    @abstractmethod
    async def write_token(self, user: models.UP) -> TokenType: ...  # pragma: no cover

    async def destroy_token(self, token: str, user: models.UP) -> None:
        access_token = await self.database.get_by_token(token)
        if access_token is not None:
            await self.database.delete(access_token)

    def _get_max_age(self) -> Optional[datetime]:
        max_age = None
        if self.lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.lifetime_seconds
            )
        return max_age

    async def _get_user_by_id(
        self, user_id: models.ID, user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def _get_token(self, token: Optional[str]) -> Optional[AP]:
        if token is None:
            return None

        return await self.database.get_by_token(token, self._get_max_age())


class DatabaseStrategy(
    BaseDatabaseStrategy[models.UP, models.ID, str, AP],
    Strategy[models.UP, models.ID],
    Generic[models.UP, models.ID, AP],
):
    async def write_token(self, user: models.UP) -> str:
        access_token_dict = self._create_access_token_dict(user)
        access_token = await self.database.create(access_token_dict)
        return access_token.token

    def _create_access_token_dict(self, user: models.UP) -> Dict[str, Any]:
        token = secrets.token_urlsafe()
        return {"token": token, "user_id": user.id}


class DatabaseRefreshStrategy(
    BaseDatabaseStrategy[models.UP, models.ID, AccessRefreshToken, APE],
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

    async def read_token_by_refresh(
        self,
        refresh_token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[models.UP]:
        if refresh_token is None:
            return None
        access_token = await self.database.get_by_refresh_token(
            refresh_token=refresh_token, max_age=self._get_max_age()
        )
        if access_token is None:
            return None
        return await self._get_user_by_id(access_token.user_id, user_manager)

    async def write_token(self, user: models.UP) -> AccessRefreshToken:
        access_token_dict = self._create_access_refresh_token_dict(user)
        token = await self.database.create(access_token_dict)
        return (token.token, token.refresh_token)

    async def destroy_token_by_refresh(
        self,
        refresh_token: Optional[str],
        user: models.UP,
    ) -> None:
        if refresh_token is not None:
            access_token = await self.database.get_by_refresh_token(
                refresh_token=refresh_token
            )
            if access_token is not None:
                await self.database.delete(access_token)

    def _create_access_refresh_token_dict(self, user: models.UP) -> Dict[str, Any]:
        access_token = secrets.token_urlsafe()
        refresh_token = secrets.token_urlsafe()
        token_dict = {
            "token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
        }
        return token_dict
