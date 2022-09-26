import secrets
from typing import Any, Optional

import pydantic
import redis.asyncio

from fastapi_users import exceptions, models
from fastapi_users.authentication.strategy.base import Strategy
from fastapi_users.authentication.token import TokenData, UserTokenData
from fastapi_users.manager import BaseUserManager


class RedisStrategy(Strategy):
    def __init__(
        self,
        redis: redis.asyncio.Redis,
        *,
        key_prefix: str = "fastapi_users_token:",
    ):
        self.redis = redis
        self.key_prefix = key_prefix

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[UserTokenData[models.UP, models.ID]]:

        if token is None:
            return None

        token_value = await self.redis.get(f"{self.key_prefix}{token}")
        if token_value is None:
            return None

        try:
            token_data = TokenData.parse_raw(token_value)
        except pydantic.ValidationError:
            return None
            
        if token_data is None:
            return None

        try:
            return await token_data.lookup_user(user_manager)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(
        self,
        token_data: UserTokenData[models.UserProtocol[Any], Any],
    ) -> str:
        token = secrets.token_urlsafe()
        expiry = (
            None
            if not token_data.time_to_expiry
            else int(token_data.time_to_expiry.total_seconds())
        )
        await self.redis.set(
            f"{self.key_prefix}{token}",
            token_data.json(),
            ex=expiry,
        )
        return token

    async def destroy_token(
        self,
        token: str,
        user: models.UserProtocol[Any],
    ) -> None:
        await self.redis.delete(f"{self.key_prefix}{token}")
