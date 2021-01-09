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
async def test_app_client_factory(
    mock_user_db, mock_authentication, after_update, get_param_test_client
) -> AsyncGenerator[httpx.AsyncClient, None]:
    async def app_factory(requires_verification):

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
            requires_verification=requires_verification,
        )

        app = FastAPI()
        app.include_router(user_router)

        return app

    async for client in get_param_test_client(app_factory):
        yield client


@pytest.mark.parametrize("requires_verification", [True, False])
@pytest.mark.router
@pytest.mark.asyncio
class TestMe:
    async def test_missing_token(
        self, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_inactive_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        inactive_user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            "/me", headers={"Authorization": f"Bearer {inactive_user.id}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_active_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            "/me", headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK
            data = cast(Dict[str, Any], response.json())
            assert data["id"] == str(user.id)
            assert data["email"] == user.email

    async def test_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            "/me", headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = cast(Dict[str, Any], response.json())
        assert data["id"] == str(verified_user.id)
        assert data["email"] == verified_user.email


@pytest.mark.parametrize("requires_verification", [True, False])
@pytest.mark.router
@pytest.mark.asyncio
class TestUpdateMe:
    async def test_missing_token(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert after_update.called is False

    async def test_inactive_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        inactive_user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            "/me", headers={"Authorization": f"Bearer {inactive_user.id}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert after_update.called is False

    async def test_empty_body(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            "/me", json={}, headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert after_update.called is False
        else:
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
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"email": "king.arthur@tintagel.bt"}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert after_update.called is False
        else:
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
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_superuser": True}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert after_update.called is False
        else:
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
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_active": False}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert after_update.called is False
        else:
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

    async def test_valid_body_is_verified(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_verified": True}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert after_update.called is False
        else:
            assert response.status_code == status.HTTP_200_OK

            data = cast(Dict[str, Any], response.json())
            assert data["is_verified"] is False

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
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        mocker.spy(mock_user_db, "update")
        current_hashed_password = user.hashed_password

        json = {"password": "merlin"}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert after_update.called is False
        else:
            assert response.status_code == status.HTTP_200_OK
            assert mock_user_db.update.called is True

            updated_user = mock_user_db.update.call_args[0][0]
            assert updated_user.hashed_password != current_hashed_password

            assert after_update.called is True
            actual_user = after_update.call_args[0][0]
            assert actual_user.id == user.id
            updated_fields = after_update.call_args[0][1]
            assert updated_fields == {"password": "merlin"}
            request = after_update.call_args[0][2]
            assert isinstance(request, Request)

    async def test_empty_body_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            "/me", json={}, headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == verified_user.email

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == verified_user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"email": "king.arthur@tintagel.bt"}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == "king.arthur@tintagel.bt"

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == verified_user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {"email": "king.arthur@tintagel.bt"}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_is_superuser_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_superuser": True}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is False

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == verified_user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_is_active_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_active": False}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == verified_user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_is_verified_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_verified": False}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_verified"] is True

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == verified_user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_password_verified_user(
        self,
        mocker,
        mock_user_db,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
        after_update,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        mocker.spy(mock_user_db, "update")
        current_hashed_password = verified_user.hashed_password

        json = {"password": "merlin"}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {verified_user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != current_hashed_password

        assert after_update.called is True
        actual_user = after_update.call_args[0][0]
        assert actual_user.id == verified_user.id
        updated_fields = after_update.call_args[0][1]
        assert updated_fields == {"password": "merlin"}
        request = after_update.call_args[0][2]
        assert isinstance(request, Request)


@pytest.mark.parametrize("requires_verification", [True, False])
@pytest.mark.router
@pytest.mark.asyncio
class TestGetUser:
    async def test_missing_token(
        self, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get("/d35d213e-f3d8-4f08-954a-7e0d1bea286f")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {verified_user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user_unverified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_not_existing_user_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            f"/{user.id}", headers={"Authorization": f"Bearer {superuser.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK

            data = cast(Dict[str, Any], response.json())
            assert data["id"] == str(user.id)
            assert "hashed_password" not in data

    async def test_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.get(
            f"/{user.id}", headers={"Authorization": f"Bearer {verified_superuser.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["id"] == str(user.id)
        assert "hashed_password" not in data


@pytest.mark.parametrize("requires_verification", [True, False])
@pytest.mark.router
@pytest.mark.asyncio
class TestUpdateUser:
    async def test_missing_token(
        self, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch("/d35d213e-f3d8-4f08-954a-7e0d1bea286f")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {verified_user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user_unverified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            json={},
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_not_existing_user_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            json={},
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_empty_body_unverified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            f"/{user.id}", json={}, headers={"Authorization": f"Bearer {superuser.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK

            data = cast(Dict[str, Any], response.json())
            assert data["email"] == user.email

    async def test_empty_body_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.patch(
            f"/{user.id}",
            json={},
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == user.email

    async def test_valid_body_unverified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"email": "king.arthur@tintagel.bt"}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK

            data = cast(Dict[str, Any], response.json())
            assert data["email"] == "king.arthur@tintagel.bt"

    async def test_valid_body_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"email": "king.arthur@tintagel.bt"}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == "king.arthur@tintagel.bt"

    async def test_valid_body_is_superuser_unverified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_superuser": True}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK

            data = cast(Dict[str, Any], response.json())
            assert data["is_superuser"] is True

    async def test_valid_body_is_superuser_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_superuser": True}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is True

    async def test_valid_body_is_active_unverified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_active": False}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK

            data = cast(Dict[str, Any], response.json())
            assert data["is_active"] is False

    async def test_valid_body_is_active_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_active": False}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is False

    async def test_valid_body_is_verified_unverified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_verified": True}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK

            data = cast(Dict[str, Any], response.json())
            assert data["is_verified"] is True

    async def test_valid_body_is_verified_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        json = {"is_verified": True}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_verified"] is True

    async def test_valid_body_password_unverified_superuser(
        self,
        mocker,
        mock_user_db,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        mocker.spy(mock_user_db, "update")
        current_hashed_password = user.hashed_password

        json = {"password": "merlin"}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_200_OK
            assert mock_user_db.update.called is True

            updated_user = mock_user_db.update.call_args[0][0]
            assert updated_user.hashed_password != current_hashed_password

    async def test_valid_body_password_verified_superuser(
        self,
        mocker,
        mock_user_db,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        mocker.spy(mock_user_db, "update")
        current_hashed_password = user.hashed_password

        json = {"password": "merlin"}
        response = await test_app_client.patch(
            f"/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != current_hashed_password


@pytest.mark.parametrize("requires_verification", [True, False])
@pytest.mark.router
@pytest.mark.asyncio
class TestDeleteUser:
    async def test_missing_token(
        self, test_app_client_factory: httpx.AsyncClient, requires_verification
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.delete("/d35d213e-f3d8-4f08-954a-7e0d1bea286f")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.delete(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_verified_user(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_user: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.delete(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {verified_user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user_unverified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.delete(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_not_existing_user_verified_superuser(
        self,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        response = await test_app_client.delete(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_unverified_superuser(
        self,
        mocker,
        mock_user_db,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        mocker.spy(mock_user_db, "delete")

        response = await test_app_client.delete(
            f"/{user.id}", headers={"Authorization": f"Bearer {superuser.id}"}
        )
        if requires_verification:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert response.json() is None
            assert mock_user_db.delete.called is True

            deleted_user = mock_user_db.delete.call_args[0][0]
            assert deleted_user.id == user.id

    async def test_verified_superuser(
        self,
        mocker,
        mock_user_db,
        test_app_client_factory: httpx.AsyncClient,
        requires_verification,
        user: UserDB,
        verified_superuser: UserDB,
    ):
        test_app_client = await test_app_client_factory(
            requires_verification
        ).__anext__()
        mocker.spy(mock_user_db, "delete")

        response = await test_app_client.delete(
            f"/{user.id}", headers={"Authorization": f"Bearer {verified_superuser.id}"}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.json() is None
        assert mock_user_db.delete.called is True

        deleted_user = mock_user_db.delete.call_args[0][0]
        assert deleted_user.id == user.id
