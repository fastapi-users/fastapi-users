import uuid
from datetime import datetime
from typing import Dict, Optional

import pytest

from fastapi_users.authentication.strategy import (
    AccessTokenDatabase,
    BaseAccessToken,
    DatabaseStrategy,
)


class AccessToken(BaseAccessToken):
    pass


class AccessTokenDatabaseMock(AccessTokenDatabase[AccessToken]):
    store: Dict[str, AccessToken]

    def __init__(self):
        self.access_token_model = AccessToken
        self.store = {}

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[AccessToken]:
        try:
            access_token = self.store[token]
            if max_age is not None and access_token.created_at < max_age:
                return None
            return access_token
        except KeyError:
            return None

    async def create(self, access_token: AccessToken) -> AccessToken:
        self.store[access_token.token] = access_token
        return access_token

    async def update(self, access_token: AccessToken) -> AccessToken:
        self.store[access_token.token] = access_token
        return access_token

    async def delete(self, access_token: AccessToken) -> None:
        try:
            del self.store[access_token.token]
        except KeyError:
            pass


@pytest.fixture
def access_token_database() -> AccessTokenDatabaseMock:
    return AccessTokenDatabaseMock()


@pytest.fixture
def database_strategy(access_token_database: AccessTokenDatabaseMock):
    return DatabaseStrategy(access_token_database, 3600)


@pytest.mark.authentication
class TestReadToken:
    @pytest.mark.asyncio
    async def test_missing_token(
        self, database_strategy: DatabaseStrategy, user_manager
    ):
        authenticated_user = await database_strategy.read_token(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self, database_strategy: DatabaseStrategy, user_manager
    ):
        authenticated_user = await database_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self,
        database_strategy: DatabaseStrategy,
        access_token_database: AccessTokenDatabaseMock,
        user_manager,
    ):
        await access_token_database.create(
            AccessToken(
                token="TOKEN", user_id=uuid.UUID("d35d213e-f3d8-4f08-954a-7e0d1bea286f")
            )
        )
        authenticated_user = await database_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self,
        database_strategy: DatabaseStrategy,
        access_token_database: AccessTokenDatabaseMock,
        user_manager,
        user,
    ):
        await access_token_database.create(AccessToken(token="TOKEN", user_id=user.id))
        authenticated_user = await database_strategy.read_token("TOKEN", user_manager)
        assert authenticated_user is not None
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token(
    database_strategy: DatabaseStrategy,
    access_token_database: AccessTokenDatabaseMock,
    user,
):
    token = await database_strategy.write_token(user)

    access_token = await access_token_database.get_by_token(token)
    assert access_token is not None
    assert access_token.user_id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_destroy_token(
    database_strategy: DatabaseStrategy,
    access_token_database: AccessTokenDatabaseMock,
    user,
):
    await access_token_database.create(AccessToken(token="TOKEN", user_id=user.id))

    await database_strategy.destroy_token("TOKEN", user)

    assert await access_token_database.get_by_token("TOKEN") is None
