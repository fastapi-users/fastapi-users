import httpx
import pytest
from fastapi import FastAPI, status

from fastapi_users.fastapi_users import FastAPIUsers
from tests.conftest import IDType, User, UserCreate, UserModel, UserUpdate


@pytest.fixture
def fastapi_users(get_user_manager, mock_authentication) -> FastAPIUsers:
    return FastAPIUsers[UserModel, IDType](get_user_manager, [mock_authentication])


@pytest.fixture
def test_app(
    fastapi_users: FastAPIUsers, secret, mock_authentication, oauth_client
) -> FastAPI:
    app = FastAPI()
    app.include_router(fastapi_users.get_register_router(User, UserCreate))
    app.include_router(fastapi_users.get_reset_password_router())
    app.include_router(fastapi_users.get_auth_router(mock_authentication))
    app.include_router(
        fastapi_users.get_oauth_router(oauth_client, mock_authentication, secret)
    )
    app.include_router(fastapi_users.get_users_router(User, UserUpdate))
    app.include_router(fastapi_users.get_verify_router(User))

    return app


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(test_app, get_test_client):
    async for client in get_test_client(test_app):
        yield client


@pytest.fixture
def openapi_dict(test_app: FastAPI):
    return test_app.openapi()


@pytest.mark.asyncio
@pytest.mark.openapi
async def test_openapi_route(test_app_client: httpx.AsyncClient):
    response = await test_app_client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK


class TestReset:
    def test_reset_password_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/reset-password"]["post"]
        assert list(route["responses"].keys()) == ["200", "400", "422"]

    def test_forgot_password_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/forgot-password"]["post"]
        assert list(route["responses"].keys()) == ["202", "422"]


class TestUsers:
    def test_patch_id_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/{id}"]["patch"]
        assert list(route["responses"].keys()) == [
            "200",
            "401",
            "403",
            "404",
            "400",
            "422",
        ]

    def test_delete_id_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/{id}"]["delete"]
        assert list(route["responses"].keys()) == ["204", "401", "403", "404", "422"]

    def test_get_id_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/{id}"]["get"]
        assert list(route["responses"].keys()) == ["200", "401", "403", "404", "422"]

    def test_patch_me_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/me"]["patch"]
        assert list(route["responses"].keys()) == ["200", "401", "400", "422"]

    def test_get_me_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/me"]["get"]
        assert list(route["responses"].keys()) == ["200", "401"]


class TestRegister:
    def test_register_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/register"]["post"]
        assert list(route["responses"].keys()) == ["201", "400", "422"]


class TestVerify:
    def test_verify_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/verify"]["post"]
        assert list(route["responses"].keys()) == ["200", "400", "422"]

    def test_request_verify_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/request-verify-token"]["post"]
        assert list(route["responses"].keys()) == ["202", "422"]


class TestOAuth2:
    def test_oauth_authorize_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/authorize"]["get"]
        assert list(route["responses"].keys()) == ["200", "422"]

    def test_oauth_callback_status_codes(self, openapi_dict):
        route = openapi_dict["paths"]["/callback"]["get"]
        assert list(route["responses"].keys()) == ["200", "400", "422"]
