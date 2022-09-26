from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import jwt
import pytest
from pydantic import SecretStr

from fastapi_users.authentication.strategy import (
    JWTStrategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.authentication.token import UserTokenData
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from tests.conftest import IDType, UserManager, UserModel

ECC_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgewlS46hocOLtT9Px
M16Y5m68xdRXMq7oSNOYhGc2kIKhRANCAATJ2SfW2ExzQCmMftxII1xLk2Ze+0WA
6ZJQA3kAZTdO8uXmCSDkTgizr39VTKSeHgeaR/cOq4/Jr5YsZrjsu0t8
-----END PRIVATE KEY-----"""

ECC_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEydkn1thMc0ApjH7cSCNcS5NmXvtF
gOmSUAN5AGU3TvLl5gkg5E4Is69/VUyknh4Hmkf3DquPya+WLGa47LtLfA==
-----END PUBLIC KEY-----"""

RSA_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAvwYzu1C2Oihk533SQ1o1zr3BscLjiw5wkCr9yYYYlK+lb8Ra
efln+JauEGhENhlG0JIlKV9KzSisGfcIZAVacdaK0PFAXtKEgZRZL7gVr3GGBPEt
y0jdQl52yKhnb1Bf5IrHBeu9jSW9WgyYDpWwop1+c9OF9QL9miO/qzkVtdILNkp4
1kvP/PldWQj8vuaxy6dGx9jRHWLFDjRERKkrUraQHs6Fmey1pDTEyN3TYWsKmi7S
mpXzgLuClEtSNgAhlwvvDyCZ8SP/SMYZIjIckZlVk+qtvrqKQdqNxJbGLrta5gtB
fWDLCDRRFsIrvfZaPsSLhuKQBv9L7ZJazTtSowIDAQABAoIBABxKZNr3ByXx2Y/X
OI61C4cE32zeOijcCJuxYki4TWen4857vBKYd2d/mWPgrUl90NkO6+YGsONVhLeL
uHhnuo9lgMWVFT113B38xICmuL91Bq4wseGLdwlfSCRLnJYFx03np7YexcHjtvlh
KBvw22oZ/SJWT16MBNcROE+5cpestErq61U6G2HpubrVIQJuNe7U9mEGZdyN1eer
zRP3eh5on7J25D3/Wtwsf8oOSWCljZ0uGLAqFVVLvxdf/By6TnCtRckCyODQ8/L0
rHq7BC5Kc5awbN5DatJEsJfnbOTNXD4dIEYjhXZ0YhtbOeh6pRN3Z7GuIC7tL8Xc
JTpKhvECgYEAzu9gnDhqiYVdjYpVWoNh9QPnxSCxvWHh38jLhLffRvXymNCXKsWQ
CNtoYyBIMve+TCLNseHN5GfTtGAh0aoWNHZC8FQwIep03y9E439EKXGMKOUuTEyL
NlIKuzOl6eIJbRaeTQ5XrIN7DhdNgKFHVC55Z+aultDrl3k3H8Xf4scCgYEA7FEP
/nqauzRScdfpExQHVskLEQe4ENvZB7r/phPQ9VnluUtnp+2I6QnN6Ye3+30rBdGk
z4gE8l1LfpK3T10qW2d6mFVTfDQ2aUR68nKR+xveEjlq5GiGIJDSA+zimMXAaGrL
KFwn/S43X86FQGegyu1OlxGfRbmZ/Xyj8gKQNUUCgYAiDDLKIWIuFFprMmqOxPU2
GhllTtbPwS4n4uLRiGtdQpRS3mcw62aifm8zeBlJAYg3ALb1YKC+xvKHSBXoaGLU
6OxknIV63xexrRZZlBQD+aHFDMhMV3/ERUVsvbe7vqwsXb9YEFcOlGeHzv+6fU6+
JBNnrAXn3KIWvyP5v1Xx+wKBgDD6cBUvNgicxIWh2UXB/e9nxapm7ihYWHf4sump
68IeOrWXwkkUuy6JgKrpHSG7hII1PDJjH5tX6MC4CdQiHBhLryYJcT8p1ykkL1M2
mbjwwqsGSXhDjaEMQurbWu+M9N7vW2HnD8ayoHlz5Tw+/h1w57v5xAgAesEF5zjO
fTL9AoGAEFTAP7v8Kw7+iSjpw5uEzEPJTpTieT7MHoyAlcCkJZOqlrgQDESuliwr
gE2YhBBk7IpPKNLttkG0p5JMCxxSoQPz0wsy/VJhuwLPtgH12Df6GFblp7B0RtgX
DCGBlAaf+d7Rd/PPf7p5lFSY+e6jOdMk/BNjpyFI73R775qjr5o=
-----END RSA PRIVATE KEY-----"""

RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvwYzu1C2Oihk533SQ1o1
zr3BscLjiw5wkCr9yYYYlK+lb8Raefln+JauEGhENhlG0JIlKV9KzSisGfcIZAVa
cdaK0PFAXtKEgZRZL7gVr3GGBPEty0jdQl52yKhnb1Bf5IrHBeu9jSW9WgyYDpWw
op1+c9OF9QL9miO/qzkVtdILNkp41kvP/PldWQj8vuaxy6dGx9jRHWLFDjRERKkr
UraQHs6Fmey1pDTEyN3TYWsKmi7SmpXzgLuClEtSNgAhlwvvDyCZ8SP/SMYZIjIc
kZlVk+qtvrqKQdqNxJbGLrta5gtBfWDLCDRRFsIrvfZaPsSLhuKQBv9L7ZJazTtS
owIDAQAB
-----END PUBLIC KEY-----"""


@pytest.fixture(params=["SECRET"])
def secret(request: pytest.FixtureRequest) -> SecretType:
    return request.param  # type: ignore


@pytest.fixture(params=["HS256"])
def algorithm(request: pytest.FixtureRequest) -> str:
    return request.param  # type: ignore


@pytest.fixture(params=[None])
def public_key(request: pytest.FixtureRequest) -> Optional[str]:
    return request.param  # type: ignore


@pytest.fixture
@pytest.mark.parametrize(
    ("algorithm", "secret", "public_key"),
    [
        ("HS256", "SECRET", None),
        ("HS256", SecretStr("SECRET"), None),
        ("RS256", RSA_PRIVATE_KEY, RSA_PUBLIC_KEY),
        ("ES256", ECC_PRIVATE_KEY, ECC_PUBLIC_KEY),
    ],
)
def jwt_strategy(algorithm: str, secret: SecretType, public_key: Optional[str]):
    if algorithm == "HS256":
        return JWTStrategy(secret)  # use default values
    else:
        return JWTStrategy(secret, algorithm=algorithm, public_key=public_key)


@pytest.fixture
def user_id(request: pytest.FixtureRequest, user: UserModel) -> Optional[UUID]:
    if hasattr(request, "param"):
        return request.param  # type: ignore
    else:
        return user.id


@pytest.fixture
def jwt_token(
    jwt_strategy: JWTStrategy,
    token_data: UserTokenData[UserModel, IDType],
    user_id: Optional[UUID],
) -> str:
    data: Dict[str, Any] = {"aud": "fastapi-users:auth"}

    if user_id is not None:
        data["sub"] = str(user_id)

    if token_data.expires_at:
        data["exp"] = int(token_data.expires_at.timestamp())

    data["iat"] = int(token_data.created_at.timestamp())
    data["auth_time"] = int(token_data.last_authenticated.timestamp())
    data["scope"] = token_data.scope

    return generate_jwt(data, jwt_strategy.encode_key, algorithm=jwt_strategy.algorithm)


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.authentication
class TestReadToken:
    @pytest.mark.asyncio
    async def test_missing_token(
        self,
        jwt_strategy: JWTStrategy,
        user_manager: UserManager,
    ):
        authenticated_user = await jwt_strategy.read_token(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self,
        jwt_strategy: JWTStrategy,
        user_manager: UserManager,
    ):
        authenticated_user = await jwt_strategy.read_token("foo", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user_id",
        [
            None,
            "foo",
            "d35d213e-f3d8-4f08-954a-7e0d1bea286f",  # non-existent user
        ],
        indirect=True,
    )
    async def test_valid_token_invalid_user(
        self,
        jwt_strategy: JWTStrategy,
        user_manager: UserManager,
        jwt_token: str,
    ):
        authenticated_user = await jwt_strategy.read_token(jwt_token, user_manager)
        assert authenticated_user is None


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.parametrize("token_expired", [False], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token(
    jwt_strategy: JWTStrategy, token_data: UserTokenData[UserModel, IDType]
):
    token = await jwt_strategy.write_token(token_data)
    decoded = decode_jwt(
        token,
        jwt_strategy.decode_key,
        audience=jwt_strategy.token_audience,
        algorithms=[jwt_strategy.algorithm],
    )
    assert decoded["sub"] == str(token_data.user.id)
    assert decoded["iat"] == int(token_data.created_at.timestamp())
    assert decoded["scope"] == token_data.scope
    assert decoded["auth_time"] == int(token_data.last_authenticated.timestamp())
    if token_data.expires_at:
        assert "exp" in decoded
        assert decoded["exp"] == int(token_data.expires_at.timestamp())


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.parametrize("token_expired", [True], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token_expired(
    jwt_strategy: JWTStrategy, token_data: UserTokenData[UserModel, IDType]
):
    token = await jwt_strategy.write_token(token_data)

    with pytest.raises(jwt.exceptions.ExpiredSignatureError):
        decode_jwt(
            token,
            jwt_strategy.decode_key,
            audience=jwt_strategy.token_audience,
            algorithms=[jwt_strategy.algorithm],
        )


def assert_token_data_approximately_equal(
    left: UserTokenData[UserModel, IDType], right: UserTokenData[UserModel, IDType]
):
    def assert_seconds_equal(left: datetime, right: datetime):
        assert left.replace(microsecond=0) == right.replace(microsecond=0)

    assert left.user == right.user
    assert left.scopes == right.scopes
    if left.expires_at and right.expires_at:
        assert_seconds_equal(left.expires_at, right.expires_at)
    else:
        assert left.expires_at == right.expires_at
    assert_seconds_equal(left.created_at, right.created_at)
    assert_seconds_equal(left.last_authenticated, right.last_authenticated)


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.parametrize("token_expired", [False], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_read_token(
    jwt_strategy: JWTStrategy,
    token_data: UserTokenData[UserModel, IDType],
    user_manager: UserManager,
):
    token = await jwt_strategy.write_token(token_data)
    decoded = await jwt_strategy.read_token(token, user_manager)
    assert decoded is not None
    assert_token_data_approximately_equal(decoded, token_data)


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.parametrize("token_expired", [True], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_read_token_expired(
    jwt_strategy: JWTStrategy,
    token_data: UserTokenData[UserModel, IDType],
    user_manager: UserManager,
):
    token = await jwt_strategy.write_token(token_data)
    decoded = await jwt_strategy.read_token(token, user_manager)
    assert decoded == None


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_destroy_token(jwt_strategy: JWTStrategy, user: UserModel):
    with pytest.raises(StrategyDestroyNotSupportedError):
        await jwt_strategy.destroy_token("TOKEN", user)
