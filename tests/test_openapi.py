import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx_oauth.clients.facebook import FacebookOAuth2
from httpx_oauth.clients.google import GoogleOAuth2

from fastapi_users import models
from fastapi_users.fastapi_users import FastAPIUsers

app = FastAPI()
users = FastAPIUsers(
    # dummy get_user_manager
    lambda: None,
    [],
    models.BaseUser,
    models.BaseUserCreate,
    models.BaseUserUpdate,
    models.BaseUserDB,
)
app.include_router(users.get_verify_router())
app.include_router(users.get_register_router())
app.include_router(users.get_users_router())
app.include_router(users.get_reset_password_router())
app.include_router(
    users.get_oauth_router(
        GoogleOAuth2(client_id="1234", client_secret="4321"), state_secret="secret"
    )
)


@pytest.fixture(scope="module")
def get_openapi_dict():
    return app.openapi()


def test_openapi_generated_ok():
    assert TestClient(app).get("/openapi.json").status_code == 200


class TestReset:
    def test_reset_password_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/reset-password"]["post"]
        assert list(route["responses"].keys()) == ["200", "400", "422"]

    def test_forgot_password_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/forgot-password"]["post"]
        assert list(route["responses"].keys()) == ["202", "422"]


class TestUsers:
    def test_patch_id_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/{id}"]["patch"]
        assert list(route["responses"].keys()) == [
            "200",
            "401",
            "403",
            "404",
            "400",
            "422",
        ]

    def test_delete_id_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/{id}"]["delete"]
        assert list(route["responses"].keys()) == ["204", "401", "403", "404", "422"]

    def test_get_id_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/{id}"]["get"]
        assert list(route["responses"].keys()) == ["200", "401", "403", "404", "422"]

    def test_patch_me_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/me"]["patch"]
        assert list(route["responses"].keys()) == ["200", "401", "400", "422"]

    def test_get_me_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/me"]["get"]
        assert list(route["responses"].keys()) == ["200", "401"]


class TestRegister:
    def test_register_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/register"]["post"]
        assert list(route["responses"].keys()) == ["201", "400", "422"]


class TestVerify:
    def test_verify_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/verify"]["post"]
        assert list(route["responses"].keys()) == ["200", "400", "422"]

    def test_request_verify_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/request-verify-token"]["post"]
        assert list(route["responses"].keys()) == ["202", "422"]


class TestOAuth2:
    def test_google_authorize_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/authorize"]["get"]
        assert list(route["responses"].keys()) == ["200", "422"]

    def test_google_callback_status_codes(self, get_openapi_dict):
        route = get_openapi_dict["paths"]["/callback"]["get"]
        assert list(route["responses"].keys()) == ["200", "400", "422"]

    def test_two_oauth_routers(self):
        a = FastAPI()
        a.include_router(
            users.get_oauth_router(
                GoogleOAuth2(client_id="1234", client_secret="4321"),
                state_secret="secret",
            ),
            prefix="/google",
        )
        a.include_router(
            users.get_oauth_router(
                FacebookOAuth2(client_id="1234", client_secret="4321"),
                state_secret="secret",
            ),
            prefix="/facebook",
        )
        assert TestClient(a).get("/openapi.json").status_code == 200
