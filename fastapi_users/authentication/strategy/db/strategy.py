import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional

from fastapi_users import exceptions, models
from fastapi_users.authentication.strategy.base import Strategy
from fastapi_users.authentication.strategy.db.adapter import AccessTokenDatabase
from fastapi_users.authentication.strategy.db.models import AP
from fastapi_users.authentication.token import TokenData, UserTokenData
from fastapi_users.manager import BaseUserManager


class DatabaseStrategy(Strategy, Generic[AP]):
    def __init__(self, database: AccessTokenDatabase[AP]):
        self.database = database

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[UserTokenData[models.UP, models.ID]]:

        if token is None:
            return None

        access_token = await self.database.get_by_token(token)
        if access_token is None:
            return None

        token_data = TokenData(
            user_id=access_token.user_id,
            created_at=access_token.created_at,
            expires_at=access_token.expires_at,
            last_authenticated=access_token.last_authenticated,
            scopes=(
                set(access_token.scopes.split(" ")) if access_token.scopes else set()
            ),
        )

        if token_data.expired:
            return None

        try:
            return await token_data.lookup_user(user_manager)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(
        self,
        token_data: UserTokenData[models.UserProtocol[Any], Any],
    ) -> str:
        access_token_dict = self._create_access_token_dict(token_data)
        access_token = await self.database.create(access_token_dict)
        return access_token.token

    async def destroy_token(
        self,
        token: str,
        user: models.UserProtocol[Any],
    ) -> None:
        access_token = await self.database.get_by_token(token)
        if access_token is not None:
            await self.database.delete(access_token)

    def _create_access_token_dict(
        self, token_data: UserTokenData[models.UP, models.ID]
    ) -> Dict[str, Any]:
        token = secrets.token_urlsafe()
        return {
            "token": token,
            "user_id": token_data.user.id,
            "scopes": token_data.scope,
            **token_data.dict(exclude={"user", "scopes"}),
        }
