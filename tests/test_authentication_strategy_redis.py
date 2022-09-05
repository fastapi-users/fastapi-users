import json
from datetime import datetime
from typing import Dict, Optional, Tuple

import pytest

from fastapi_users.authentication.strategy import RedisStrategy
from fastapi_users.authentication.token import UserTokenData
from tests.conftest import IDType, UserManager, UserModel


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
    return RedisStrategy(redis)


@pytest.mark.authentication
class TestReadToken:
    @pytest.mark.asyncio
    async def test_missing_token(self, redis_strategy: RedisStrategy, user_manager):
        authenticated_user = await redis_strategy.read_token(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(self, redis_strategy: RedisStrategy, user_manager):
        authenticated_user = await redis_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_invalid_uuid(
        self,
        redis_strategy: RedisStrategy,
        redis: RedisMock,
        user_manager,
    ):
        await redis.set(f"{redis_strategy.key_prefix}TOKEN", "bar")
        authenticated_user = await redis_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self,
        redis_strategy: RedisStrategy,
        redis: RedisMock,
        user_manager,
    ):
        await redis.set(
            f"{redis_strategy.key_prefix}TOKEN", "d35d213e-f3d8-4f08-954a-7e0d1bea286f"
        )
        authenticated_user = await redis_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None


@pytest.mark.parametrize("token_expired", [False], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token(
    redis_strategy: RedisStrategy,
    redis: RedisMock,
    token_data: UserTokenData[UserModel, IDType],
):
    token = await redis_strategy.write_token(token_data)

    token_value = await redis.get(f"{redis_strategy.key_prefix}{token}")
    assert token_value is not None

    decoded = json.loads(token_value)

    assert decoded["user_id"] == str(token_data.user.id)
    assert set(decoded["scopes"]) == token_data.scopes

    assert datetime.fromisoformat(decoded["created_at"]) == token_data.created_at

    assert (
        datetime.fromisoformat(decoded["last_authenticated"])
        == token_data.last_authenticated
    )

    if token_data.expires_at:
        assert "expires_at" in decoded
        assert datetime.fromisoformat(decoded["expires_at"]) == token_data.expires_at


@pytest.mark.parametrize("token_expired", [True], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token_expired(
    redis_strategy: RedisStrategy,
    redis: RedisMock,
    token_data: UserTokenData[UserModel, IDType],
):
    token = await redis_strategy.write_token(token_data)

    value = await redis.get(f"{redis_strategy.key_prefix}{token}")
    assert value is None


@pytest.mark.parametrize("token_expired", [False], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_read_token(
    redis_strategy: RedisStrategy,
    redis: RedisMock,
    token_data: UserTokenData[UserModel, IDType],
    user_manager: UserManager,
):
    token = await redis_strategy.write_token(token_data)
    retrieved_token_data = await redis_strategy.read_token(token, user_manager)
    assert retrieved_token_data == token_data


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_destroy_token(
    redis_strategy: RedisStrategy, redis: RedisMock, user: UserModel
):
    await redis.set(f"{redis_strategy.key_prefix}TOKEN", str(user.id))

    await redis_strategy.destroy_token("TOKEN", user)

    assert await redis.get(f"{redis_strategy.key_prefix}TOKEN") is None
