import pytest
from jwt import ExpiredSignatureError

from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt


@pytest.mark.jwt
def test_generate_decode_jwt(secret: SecretType):
    audience = "TEST_AUDIENCE"
    data = {"foo": "bar", "aud": audience}

    jwt = generate_jwt(data, secret, 3600)
    decoded = decode_jwt(jwt, secret, [audience])

    assert decoded["foo"] == "bar"
    assert decoded["aud"] == audience


@pytest.mark.jwt
def test_generate_jwt_zero_lifetime_is_expired(secret: SecretType):
    token = generate_jwt({"aud": "TEST_AUDIENCE"}, secret, 0)

    with pytest.raises(ExpiredSignatureError):
        decode_jwt(token, secret, ["TEST_AUDIENCE"])


@pytest.mark.jwt
def test_generate_jwt_without_lifetime_has_no_exp(secret: SecretType):
    token = generate_jwt({"aud": "TEST_AUDIENCE"}, secret, None)

    assert "exp" not in decode_jwt(token, secret, ["TEST_AUDIENCE"])
