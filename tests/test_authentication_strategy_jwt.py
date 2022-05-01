import pytest

from fastapi_users.authentication.strategy import (
    JWTStrategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from tests.conftest import IDType, UserModel

LIFETIME = 3600

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


@pytest.fixture
def jwt_strategy(request, secret: SecretType):
    if request.param == "HS256":
        return JWTStrategy(secret, LIFETIME)
    elif request.param == "RS256":
        return JWTStrategy(
            RSA_PRIVATE_KEY, LIFETIME, algorithm="RS256", public_key=RSA_PUBLIC_KEY
        )
    elif request.param == "ES256":
        return JWTStrategy(
            ECC_PRIVATE_KEY, LIFETIME, algorithm="ES256", public_key=ECC_PUBLIC_KEY
        )
    raise ValueError(f"Unrecognized algorithm: {request.param}")


@pytest.fixture
def token(jwt_strategy: JWTStrategy[UserModel, IDType]):
    def _token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:auth"}
        if user_id is not None:
            data["user_id"] = str(user_id)
        return generate_jwt(
            data, jwt_strategy.encode_key, lifetime, algorithm=jwt_strategy.algorithm
        )

    return _token


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.authentication
class TestReadToken:
    @pytest.mark.asyncio
    async def test_missing_token(
        self, jwt_strategy: JWTStrategy[UserModel, IDType], user_manager
    ):
        authenticated_user = await jwt_strategy.read_token(None, user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_invalid_token(
        self, jwt_strategy: JWTStrategy[UserModel, IDType], user_manager
    ):
        authenticated_user = await jwt_strategy.read_token("foo", user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_missing_user_payload(
        self, jwt_strategy: JWTStrategy[UserModel, IDType], user_manager, token
    ):
        authenticated_user = await jwt_strategy.read_token(token(), user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_invalid_uuid(
        self, jwt_strategy: JWTStrategy[UserModel, IDType], user_manager, token
    ):
        authenticated_user = await jwt_strategy.read_token(token("foo"), user_manager)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token_not_existing_user(
        self, jwt_strategy: JWTStrategy[UserModel, IDType], user_manager, token
    ):
        authenticated_user = await jwt_strategy.read_token(
            token("d35d213e-f3d8-4f08-954a-7e0d1bea286f"), user_manager
        )
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_valid_token(
        self, jwt_strategy: JWTStrategy[UserModel, IDType], user_manager, token, user
    ):
        authenticated_user = await jwt_strategy.read_token(token(user.id), user_manager)
        assert authenticated_user is not None
        assert authenticated_user.id == user.id


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_write_token(jwt_strategy: JWTStrategy[UserModel, IDType], user):
    token = await jwt_strategy.write_token(user)

    decoded = decode_jwt(
        token,
        jwt_strategy.decode_key,
        audience=jwt_strategy.token_audience,
        algorithms=[jwt_strategy.algorithm],
    )
    assert decoded["user_id"] == str(user.id)


@pytest.mark.parametrize("jwt_strategy", ["HS256", "RS256", "ES256"], indirect=True)
@pytest.mark.authentication
@pytest.mark.asyncio
async def test_destroy_token(jwt_strategy: JWTStrategy[UserModel, IDType], user):
    with pytest.raises(StrategyDestroyNotSupportedError):
        await jwt_strategy.destroy_token("TOKEN", user)
