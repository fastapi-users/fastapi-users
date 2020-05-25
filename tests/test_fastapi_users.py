import pytest
import httpx
from fastapi import Depends, FastAPI, status

from fastapi_users import FastAPIUsers
from tests.conftest import User, UserCreate, UserUpdate, UserDB


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    mock_user_db, mock_authentication, oauth_client, get_test_client
) -> httpx.AsyncClient:
    fastapi_users = FastAPIUsers(
        mock_user_db, [mock_authentication], User, UserCreate, UserUpdate, UserDB,
    )

    app = FastAPI()
    app.include_router(fastapi_users.get_register_router())
    app.include_router(fastapi_users.get_reset_password_router("SECRET"))
    app.include_router(fastapi_users.get_auth_router(mock_authentication))
    app.include_router(fastapi_users.get_oauth_router(oauth_client, "SECRET"))
    app.include_router(fastapi_users.get_users_router(), prefix="/users")

    @app.get("/current-user")
    def current_user(user=Depends(fastapi_users.get_current_user)):
        return user

    @app.get("/current-active-user")
    def current_active_user(user=Depends(fastapi_users.get_current_active_user)):
        return user

    @app.get("/current-superuser")
    def current_superuser(user=Depends(fastapi_users.get_current_superuser)):
        return user

    @app.get("/optional-current-user")
    def optional_current_user(user=Depends(fastapi_users.get_optional_current_user)):
        return user

    @app.get("/optional-current-active-user")
    def optional_current_active_user(
        user=Depends(fastapi_users.get_optional_current_active_user),
    ):
        return user

    @app.get("/optional-current-superuser")
    def optional_current_superuser(
        user=Depends(fastapi_users.get_optional_current_superuser),
    ):
        return user

    return await get_test_client(app)


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestRoutes:
    async def test_routes_exist(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post("/register")
        assert response.status_code not in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        response = await test_app_client.post("/forgot-password")
        assert response.status_code not in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        response = await test_app_client.post("/reset-password")
        assert response.status_code not in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        response = await test_app_client.post("/login")
        assert response.status_code not in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        response = await test_app_client.post("/logout")
        assert response.status_code not in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        response = await test_app_client.get("/users/aaa")
        assert response.status_code not in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        response = await test_app_client.patch("/users/aaa")
        assert response.status_code not in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.get(
            "/current-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentActiveUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-active-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-active-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserDB
    ):
        response = await test_app_client.get(
            "/current-active-user",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.get(
            "/current-active-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentSuperuser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-superuser")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserDB
    ):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_valid_token_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": f"Bearer {superuser.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-user")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.get(
            "/optional-current-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentActiveUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-active-user")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-active-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserDB
    ):
        response = await test_app_client.get(
            "/optional-current-active-user",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.get(
            "/optional-current-active-user",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentSuperuser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-superuser")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserDB
    ):
        response = await test_app_client.get(
            "/optional-current-superuser",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.get(
            "/optional-current-superuser",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None
