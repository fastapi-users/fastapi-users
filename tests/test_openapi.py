import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import fastapi_users.authentication
from fastapi_users import models
from fastapi_users.fastapi_users import FastAPIUsers

app = FastAPI()
jwt_authentication = fastapi_users.authentication.JWTAuthentication(
    secret="", lifetime_seconds=3600
)
cookie_authentication = fastapi_users.authentication.CookieAuthentication(secret="")
users = FastAPIUsers(
    # dummy get_user_manager
    lambda: None,
    [cookie_authentication, jwt_authentication],
    models.BaseUser,
    models.BaseUserCreate,
    models.BaseUserUpdate,
    models.BaseUserDB,
)
app.include_router(users.get_verify_router())
app.include_router(users.get_register_router())
app.include_router(users.get_users_router())
app.include_router(users.get_reset_password_router())
# app.include_router(users.get_oauth_router())
app.include_router(users.get_auth_router(jwt_authentication), prefix="/jwt")
app.include_router(users.get_auth_router(cookie_authentication), prefix="/cookie")


@pytest.fixture(scope="module")
def get_openapi_dict():
    return app.openapi()


def test_openapi_generated_ok():
    assert TestClient(app).get("/openapi.json").status_code == 200


class TestLogin:
    def test_jwt_login_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/jwt/login"]["post"]
        assert ["200", "400", "422"] == list(route["responses"].keys())

    def test_jwt_login_200_body(self, get_openapi_dict):
        """Check if example is up to date"""
        example = get_openapi_dict["paths"]["/jwt/login"]["post"]["responses"]["200"][
            "content"
        ]["application/json"]["example"]
        assert (
            fastapi_users.authentication.jwt.JWTLoginResponse.schema()[
                "properties"
            ].keys()
            == example.keys()
        )

    def test_cookie_login_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/cookie/login"]["post"]
        assert ["200", "400", "422"] == list(route["responses"].keys())


class TestLogout:
    def test_cookie_logout_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/cookie/logout"]["post"]
        assert ["200", "401"] == list(route["responses"].keys())


class TestReset:
    def test_reset_password_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/reset-password"]["post"]
        assert ["200", "400", "422"] == list(route["responses"].keys())

    def test_forgot_password_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/forgot-password"]["post"]
        assert ["202", "422"] == list(route["responses"].keys())

