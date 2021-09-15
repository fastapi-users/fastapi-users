import pytest

from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt


@pytest.mark.jwt
def test_generate_decode_jwt(secret: SecretType):
    audience = "TEST_AUDIENCE"
    data = {"foo": "bar", "aud": audience}

    jwt = generate_jwt(data, secret, 3600)
    decoded = decode_jwt(jwt, secret, [audience])

    assert decoded["foo"] == "bar"
    assert decoded["aud"] == audience
