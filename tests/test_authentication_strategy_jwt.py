import pytest

from fastapi_users.authentication.strategy import (
    JWTStrategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt

LIFETIME = 3600


@pytest.fixture
def jwt_strategy(secret: SecretType):
    return JWTStrategy(secret, LIFETIME)


@pytest.fixture
def token(secret):
    def _token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user_id is not None:
            data["user_id"] = str(user_id)
        return generate_jwt(data, secret, lifetime)

    return _token


@pytest.mark.authentication
class TestReadToken:
    @pytest.mark.asyncio
    async def test_missing_token(self, jwt_strategy: JWTStrategy, user_manager):
        authenticated_user = await jwt_strategy.read_token(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(self, jwt_strategy: JWTStrategy, user_manager):
        authenticated_user = await jwt_strategy.read_token("foo", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_missing_user_payload(
        self, jwt_strategy: JWTStrategy, user_manager, token
    ):
        authenticated_user = await jwt_strategy.read_token(token(), user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_invalid_uuid(
        self, jwt_strategy: JWTStrategy, user_manager, token
    ):
        authenticated_user = await jwt_strategy.read_token(token("foo"), user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self, jwt_strategy: JWTStrategy, user_manager, token
    ):
        authenticated_user = await jwt_strategy.read_token(
            token("d35d213e-f3d8-4f08-954a-7e0d1bea286f"), user_manager
        )
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self, jwt_strategy: JWTStrategy, user_manager, token, user
    ):
        authenticated_user = await jwt_strategy.read_token(token(user.id), user_manager)
        assert authenticated_user is not None
        assert authenticated_user.id == user.id


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token(jwt_strategy: JWTStrategy, user):
    token = await jwt_strategy.write_token(user)

    decoded = decode_jwt(
        token, jwt_strategy.secret, audience=jwt_strategy.token_audience
    )
    assert decoded["user_id"] == str(user.id)


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_destroy_token(jwt_strategy: JWTStrategy, user):
    with pytest.raises(StrategyDestroyNotSupportedError):
        await jwt_strategy.destroy_token("TOKEN", user)
