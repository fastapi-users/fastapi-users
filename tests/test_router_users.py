from typing import Any, AsyncGenerator, Dict, cast
from unittest.mock import MagicMock

import asynctest
import httpx
import pytest
from fastapi import FastAPI, Request, status

from fastapi_users.authentication import Authenticator
from fastapi_users.router import get_users_router
from tests.conftest import MockAuthentication, User, UserDB, UserUpdate

SECRET = "SECRET"
LIFETIME = 3600


def after_update_sync():
    return MagicMock(return_value=None)


def after_update_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[after_update_sync, after_update_async])
def after_update(request):
    return request.param()


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    mock_user_db, mock_authentication, after_update, get_test_client
) -> AsyncGenerator[httpx.AsyncClient, None]:
    mock_authentication_bis = MockAuthentication(name="mock-bis")
    authenticator = Authenticator(
        [mock_authentication, mock_authentication_bis], mock_user_db
    )

    user_router = get_users_router(
        mock_user_db,
        User,
        UserUpdate,
        UserDB,
        authenticator,
        after_update,
    )

    app = FastAPI()
    app.include_router(user_router)

    async for client in get_test_client(app):
        yield client


@pytest.mark.router
@pytest.mark.asyncio
class TestMe:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserDB
    ):
        response = await test_app_client.get(
            "/me", headers={"Authorization": f"Bearer {inactive_user.id}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_active_user(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.get(
            "/me", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["id"] == str(user.id)
        assert data["email"] == user.email


@pytest.mark.router
@pytest.mark.asyncio
class TestUpdateMe:
    async def test_missing_token(
        self, test_app_client: httpx.AsyncClient, after_update
    ):
        response = await test_app_client.patch("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert after_update.called is False

    async def test_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserDB, after_update
    ):
        response = await test_app_client.patch(
            "/me", headers={"Authorization": f"Bearer {inactive_user.id}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert after_update.called is False

    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, user: UserDB, after_update
    ):
        response = await test_app_client.patch(
            "/me", json={}, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == user.email

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body(
        self, test_app_client: httpx.AsyncClient, user: UserDB, after_update
    ):
        json = {"email": "king.arthur@tintagel.bt"}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == "king.arthur@tintagel.bt"

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {"email": "king.arthur@tintagel.bt"}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_is_superuser(
        self, test_app_client: httpx.AsyncClient, user: UserDB, after_update
    ):
        json = {"is_superuser": True}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is False

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_is_active(
        self, test_app_client: httpx.AsyncClient, user: UserDB, after_update
    ):
        json = {"is_active": False}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_password(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        after_update,
    ):
        mocker.spy(mock_user_db, "update")
        current_hashed_passord = user.hashed_password

        json = {"password": "merlin"}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != current_hashed_passord

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {"password": "merlin"}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)


@pytest.mark.router
@pytest.mark.asyncio
class TestGetUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/d35d213e-f3d8-4f08-954a-7e0d1bea286f")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.get(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.get(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_superuser(
        self, test_app_client: httpx.AsyncClient, user: UserDB, superuser: UserDB
    ):
        response = await test_app_client.get(
            f"/{user.id}", headers={"Authorization": f"Bearer {superuser.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["id"] == str(user.id)
        assert "hashed_password" not in data


@pytest.mark.router
@pytest.mark.asyncio
class TestUpdateUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.patch("/d35d213e-f3d8-4f08-954a-7e0d1bea286f")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.patch(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.patch(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            json={},
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, user: UserDB, superuser: UserDB
    ):
        response = await test_app_client.patch(
            f"/{user.id}", json={}, headers={"Authorization": f"Bearer {superuser.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == user.email

    async def test_valid_body(
        self, test_app_client: httpx.AsyncClient, user: UserDB, superuser: UserDB
    ):
        json = {"email": "king.arthur@tintagel.bt"}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == "king.arthur@tintagel.bt"

    async def test_valid_body_is_superuser(
        self, test_app_client: httpx.AsyncClient, user: UserDB, superuser: UserDB
    ):
        json = {"is_superuser": True}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is True

    async def test_valid_body_is_active(
        self, test_app_client: httpx.AsyncClient, user: UserDB, superuser: UserDB
    ):
        json = {"is_active": False}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is False

    async def test_valid_body_password(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        superuser: UserDB,
    ):
        mocker.spy(mock_user_db, "update")
        current_hashed_passord = user.hashed_password

        json = {"password": "merlin"}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != current_hashed_passord


@pytest.mark.router
@pytest.mark.asyncio
class TestDeleteUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.delete("/d35d213e-f3d8-4f08-954a-7e0d1bea286f")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.delete(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.delete(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_superuser(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        superuser: UserDB,
    ):
        mocker.spy(mock_user_db, "delete")

        response = await test_app_client.delete(
            f"/{user.id}", headers={"Authorization": f"Bearer {superuser.id}"}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.json() is None
        assert mock_user_db.delete.called is True

        deleted_user = mock_user_db.delete.call_args[0][0]
        assert deleted_user.id == user.id
