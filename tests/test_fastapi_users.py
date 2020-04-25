import pytest
import httpx
from fastapi import Depends, FastAPI
from httpx_oauth.oauth2 import OAuth2
from starlette import status

from fastapi_users import FastAPIUsers
from fastapi_users.router import Event, EventHandlersRouter
from tests.conftest import User, UserCreate, UserUpdate, UserDB


def sync_event_handler():
    return None


async def async_event_handler():
    return None


@pytest.fixture(params=[sync_event_handler, async_event_handler])
def fastapi_users(
    request, mock_user_db, mock_authentication, oauth_client
) -> FastAPIUsers:
    fastapi_users = FastAPIUsers(
        mock_user_db,
        [mock_authentication],
        User,
        UserCreate,
        UserUpdate,
        UserDB,
        "SECRET",
    )

    fastapi_users.get_oauth_router(oauth_client, "SECRET")

    @fastapi_users.on_after_register()
    def on_after_register():
        return request.param()

    @fastapi_users.on_after_forgot_password()
    def on_after_forgot_password():
        return request.param()

    @fastapi_users.on_after_update()
    def on_after_update():
        return request.param()

    return fastapi_users


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(fastapi_users, get_test_client) -> httpx.AsyncClient:
    app = FastAPI()
    app.include_router(fastapi_users.router, prefix="/users")

    @app.get("/current-user")
    def current_user(user=Depends(fastapi_users.get_current_user)):
        return user

    @app.get("/current-active-user")
    def current_active_user(user=Depends(fastapi_users.get_current_active_user)):
        return user

    @app.get("/current-superuser")
    def current_superuser(user=Depends(fastapi_users.get_current_superuser)):
        return user

    return await get_test_client(app)


@pytest.mark.fastapi_users
class TestFastAPIUsers:
    def test_event_handlers(self, fastapi_users):
        event_handlers = fastapi_users.router.event_handlers
        assert len(event_handlers[Event.ON_AFTER_REGISTER]) == 1
        assert len(event_handlers[Event.ON_AFTER_FORGOT_PASSWORD]) == 1


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestRouter:
    async def test_routes_exist(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post("/users/register")
        assert response.status_code != status.HTTP_404_NOT_FOUND

        response = await test_app_client.post("/users/login")
        assert response.status_code != status.HTTP_404_NOT_FOUND

        response = await test_app_client.post("/users/forgot-password")
        assert response.status_code != status.HTTP_404_NOT_FOUND

        response = await test_app_client.post("/users/reset-password")
        assert response.status_code != status.HTTP_404_NOT_FOUND

        response = await test_app_client.get("/users/aaa")
        assert response.status_code != status.HTTP_404_NOT_FOUND

        response = await test_app_client.patch("/users/aaa")
        assert response.status_code != status.HTTP_404_NOT_FOUND


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
def test_get_oauth_router(mocker, fastapi_users: FastAPIUsers, oauth_client: OAuth2):
    # Check that existing OAuth router declared
    # before the handlers decorators is correctly binded
    existing_oauth_router = fastapi_users.oauth_routers[0]
    event_handlers = existing_oauth_router.event_handlers
    assert len(event_handlers[Event.ON_AFTER_REGISTER]) == 1
    assert len(event_handlers[Event.ON_AFTER_FORGOT_PASSWORD]) == 1

    # Check that OAuth router declared
    # after the handlers decorators is correctly binded
    oauth_router = fastapi_users.get_oauth_router(oauth_client, "SECRET")
    assert isinstance(oauth_router, EventHandlersRouter)
    event_handlers = oauth_router.event_handlers
    assert len(event_handlers[Event.ON_AFTER_REGISTER]) == 1
    assert len(event_handlers[Event.ON_AFTER_FORGOT_PASSWORD]) == 1
