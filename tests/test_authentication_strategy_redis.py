from datetime import datetime
from typing import Dict, Optional, Tuple

import pytest

from fastapi_users.authentication.strategy import RedisStrategy
from tests.conftest import IDType, UserModel


class RedisMock:
    store: Dict[str, Tuple[str, Optional[int]]]

    def __init__(self):
        self.store = {}

    async def get(self, key: str) -> Optional[str]:
        try:
            value, expiration = self.store[key]
            if expiration is not None and expiration < datetime.now().timestamp():
                return None
            return value
        except KeyError:
            return None

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        expiration = None
        if ex is not None:
            expiration = int(datetime.now().timestamp() + ex)
        self.store[key] = (value, expiration)

    async def delete(self, key: str):
        try:
            del self.store[key]
        except KeyError:
            pass


@pytest.fixture
def redis() -> RedisMock:
    return RedisMock()


@pytest.fixture
def redis_strategy(redis):
    return RedisStrategy(redis, 3600)


@pytest.mark.authentication
class TestReadToken:
    @pytest.mark.asyncio
    async def test_missing_token(
        self, redis_strategy: RedisStrategy[UserModel, IDType], user_manager
    ):
        authenticated_user = await redis_strategy.read_token(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self, redis_strategy: RedisStrategy[UserModel, IDType], user_manager
    ):
        authenticated_user = await redis_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_invalid_uuid(
        self,
        redis_strategy: RedisStrategy[UserModel, IDType],
        redis: RedisMock,
        user_manager,
    ):
        await redis.set("TOKEN", "bar")
        authenticated_user = await redis_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self,
        redis_strategy: RedisStrategy[UserModel, IDType],
        redis: RedisMock,
        user_manager,
    ):
        await redis.set("TOKEN", "d35d213e-f3d8-4f08-954a-7e0d1bea286f")
        authenticated_user = await redis_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self,
        redis_strategy: RedisStrategy[UserModel, IDType],
        redis: RedisMock,
        user_manager,
        user,
    ):
        await redis.set("TOKEN", str(user.id))
        authenticated_user = await redis_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is not None
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token(
    redis_strategy: RedisStrategy[UserModel, IDType], redis: RedisMock, user
):
    token = await redis_strategy.write_token(user)

    value = await redis.get(token)
    assert value == str(user.id)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_destroy_token(
    redis_strategy: RedisStrategy[UserModel, IDType], redis: RedisMock, user
):
    await redis.set("TOKEN", str(user.id))

    await redis_strategy.destroy_token("TOKEN", user)

    assert await redis.get("TOKEN") is None
