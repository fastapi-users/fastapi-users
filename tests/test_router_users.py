from typing import cast, Dict, Any
from unittest.mock import MagicMock

import asynctest
import httpx
import jwt
import pytest
from fastapi import FastAPI
from starlette import status
from starlette.requests import Request

from fastapi_users.authentication import Authenticator
from fastapi_users.router import ErrorCode, Event, get_user_router
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt
from tests.conftest import MockAuthentication, User, UserCreate, UserUpdate, UserDB

SECRET = "SECRET"
LIFETIME = 3600


@pytest.fixture
def forgot_password_token():
    def _forgot_password_token(user_id=None, lifetime=LIFETIME):
        data = {"aud": "fastapi-users:reset"}
        if user_id is not None:
            data["user_id"] = user_id
        return generate_jwt(data, lifetime, SECRET, JWT_ALGORITHM)

    return _forgot_password_token


def event_handler_sync():
    return MagicMock(return_value=None)


def event_handler_async():
    return asynctest.CoroutineMock(return_value=None)


@pytest.fixture(params=[event_handler_sync, event_handler_async])
def event_handler(request):
    return request.param()


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    mock_user_db, mock_authentication, event_handler, get_test_client
) -> httpx.AsyncClient:
    mock_authentication_bis = MockAuthentication(name="mock-bis")
    authenticator = Authenticator(
        [mock_authentication, mock_authentication_bis], mock_user_db
    )

    user_router = get_user_router(
        mock_user_db,
        User,
        UserCreate,
        UserUpdate,
        UserDB,
        authenticator,
        SECRET,
        LIFETIME,
    )

    user_router.add_event_handler(Event.ON_AFTER_REGISTER, event_handler)
    user_router.add_event_handler(Event.ON_AFTER_FORGOT_PASSWORD, event_handler)
    user_router.add_event_handler(Event.ON_AFTER_UPDATE, event_handler)

    app = FastAPI()
    app.include_router(user_router)

    return await get_test_client(app)


@pytest.mark.router
@pytest.mark.asyncio
class TestRegister:
    async def test_empty_body(self, test_app_client: httpx.AsyncClient, event_handler):
        response = await test_app_client.post("/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert event_handler.called is False

    async def test_missing_password(
        self, test_app_client: httpx.AsyncClient, event_handler
    ):
        json = {"email": "king.arthur@camelot.bt"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert event_handler.called is False

    async def test_wrong_email(self, test_app_client: httpx.AsyncClient, event_handler):
        json = {"email": "king.arthur", "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert event_handler.called is False

    async def test_existing_user(
        self, test_app_client: httpx.AsyncClient, event_handler
    ):
        json = {"email": "king.arthur@camelot.bt", "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS
        assert event_handler.called is False

    async def test_valid_body(self, test_app_client: httpx.AsyncClient, event_handler):
        json = {"email": "lancelot@camelot.bt", "password": "guinevere"}
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert event_handler.called is True

        data = cast(Dict[str, Any], response.json())
        assert "hashed_password" not in data
        assert "password" not in data
        assert data["id"] is not None

        actual_user = event_handler.call_args[0][0]
        assert actual_user.id == data["id"]
        request = event_handler.call_args[0][1]
        assert isinstance(request, Request)

    async def test_valid_body_is_superuser(
        self, test_app_client: httpx.AsyncClient, event_handler
    ):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
            "is_superuser": True,
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert event_handler.called is True

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is False

    async def test_valid_body_is_active(
        self, test_app_client: httpx.AsyncClient, event_handler
    ):
        json = {
            "email": "lancelot@camelot.bt",
            "password": "guinevere",
            "is_active": False,
        }
        response = await test_app_client.post("/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED
        assert event_handler.called is True

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True


@pytest.mark.router
@pytest.mark.parametrize("path", ["/login/mock", "/login/mock-bis"])
@pytest.mark.asyncio
class TestLogin:
    async def test_empty_body(self, path, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post(path, data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_username(self, path, test_app_client: httpx.AsyncClient):
        data = {"password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(self, path, test_app_client: httpx.AsyncClient):
        data = {"username": "king.arthur@camelot.bt"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_not_existing_user(self, path, test_app_client: httpx.AsyncClient):
        data = {"username": "lancelot@camelot.bt", "password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS

    async def test_wrong_password(self, path, test_app_client: httpx.AsyncClient):
        data = {"username": "king.arthur@camelot.bt", "password": "percival"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS

    async def test_valid_credentials(
        self, path, test_app_client: httpx.AsyncClient, user: UserDB
    ):
        data = {"username": "king.arthur@camelot.bt", "password": "guinevere"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"token": user.id}

    async def test_inactive_user(self, path, test_app_client: httpx.AsyncClient):
        data = {"username": "percival@camelot.bt", "password": "angharad"}
        response = await test_app_client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS


@pytest.mark.router
@pytest.mark.parametrize("path", ["/logout/mock", "/logout/mock-bis"])
@pytest.mark.asyncio
class TestLogout:
    async def test_missing_token(self, path, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_unimplemented_logout(
        self, mocker, path, test_app_client: httpx.AsyncClient, user: UserDB
    ):
        get_logout_response_spy = mocker.spy(MockAuthentication, "get_logout_response")
        response = await test_app_client.post(
            path, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED

        get_logout_response_spy.assert_called_once()


@pytest.mark.router
@pytest.mark.asyncio
class TestForgotPassword:
    async def test_empty_body(self, test_app_client: httpx.AsyncClient, event_handler):
        response = await test_app_client.post("/forgot-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert event_handler.called is False

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, event_handler
    ):
        json = {"email": "lancelot@camelot.bt"}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert event_handler.called is False

    async def test_inactive_user(
        self, test_app_client: httpx.AsyncClient, event_handler
    ):
        json = {"email": "percival@camelot.bt"}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert event_handler.called is False

    async def test_existing_user(
        self, test_app_client: httpx.AsyncClient, event_handler, user
    ):
        json = {"email": "king.arthur@camelot.bt"}
        response = await test_app_client.post("/forgot-password", json=json)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert event_handler.called is True

        actual_user = event_handler.call_args[0][0]
        assert actual_user.id == user.id
        actual_token = event_handler.call_args[0][1]
        decoded_token = jwt.decode(
            actual_token,
            SECRET,
            audience="fastapi-users:reset",
            algorithms=[JWT_ALGORITHM],
        )
        assert decoded_token["user_id"] == user.id
        request = event_handler.call_args[0][2]
        assert isinstance(request, Request)


@pytest.mark.router
@pytest.mark.asyncio
class TestResetPassword:
    async def test_empty_body(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post("/reset-password", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        json = {"password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(self, test_app_client: httpx.AsyncClient):
        json = {"token": "foo"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        json = {"token": "foo", "password": "guinevere"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN

    async def test_valid_token_missing_user_id_payload(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        forgot_password_token,
    ):
        mocker.spy(mock_user_db, "update")

        json = {"token": forgot_password_token(), "password": "holygrail"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN
        assert mock_user_db.update.called is False

    async def test_inactive_user(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        forgot_password_token,
        inactive_user: UserDB,
    ):
        mocker.spy(mock_user_db, "update")

        json = {
            "token": forgot_password_token(inactive_user.id),
            "password": "holygrail",
        }
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.RESET_PASSWORD_BAD_TOKEN
        assert mock_user_db.update.called is False

    async def test_existing_user(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        forgot_password_token,
        user: UserDB,
    ):
        mocker.spy(mock_user_db, "update")
        current_hashed_passord = user.hashed_password

        json = {"token": forgot_password_token(user.id), "password": "holygrail"}
        response = await test_app_client.post("/reset-password", json=json)
        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != current_hashed_passord


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
        assert data["id"] == user.id
        assert data["email"] == user.email


@pytest.mark.router
@pytest.mark.asyncio
class TestUpdateMe:
    async def test_missing_token(
        self, test_app_client: httpx.AsyncClient, event_handler
    ):
        response = await test_app_client.patch("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert event_handler.called is False

    async def test_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserDB, event_handler
    ):
        response = await test_app_client.patch(
            "/me", headers={"Authorization": f"Bearer {inactive_user.id}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert event_handler.called is False

    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, user: UserDB, event_handler
    ):
        response = await test_app_client.patch(
            "/me", json={}, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == user.email

        assert event_handler.called is True
        actual_user = event_handler.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = event_handler.call_args[0][1]
        assert updated_fields == {}
        request = event_handler.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body(
        self, test_app_client: httpx.AsyncClient, user: UserDB, event_handler
    ):
        json = {"email": "king.arthur@tintagel.bt"}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["email"] == "king.arthur@tintagel.bt"

        assert event_handler.called is True
        actual_user = event_handler.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = event_handler.call_args[0][1]
        assert updated_fields == {"email": "king.arthur@tintagel.bt"}
        request = event_handler.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_is_superuser(
        self, test_app_client: httpx.AsyncClient, user: UserDB, event_handler
    ):
        json = {"is_superuser": True}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is False

        assert event_handler.called is True
        actual_user = event_handler.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = event_handler.call_args[0][1]
        assert updated_fields == {}
        request = event_handler.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_is_active(
        self, test_app_client: httpx.AsyncClient, user: UserDB, event_handler
    ):
        json = {"is_active": False}
        response = await test_app_client.patch(
            "/me", json=json, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True

        assert event_handler.called is True
        actual_user = event_handler.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = event_handler.call_args[0][1]
        assert updated_fields == {}
        request = event_handler.call_args[0][2]
        assert isinstance(request, Request)

    async def test_valid_body_password(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        user: UserDB,
        event_handler,
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

        assert event_handler.called is True
        actual_user = event_handler.call_args[0][0]
        assert actual_user.id == user.id
        updated_fields = event_handler.call_args[0][1]
        assert updated_fields == {"password": "merlin"}
        request = event_handler.call_args[0][2]
        assert isinstance(request, Request)


@pytest.mark.router
@pytest.mark.asyncio
class TestListUsers:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.get(
            "/", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.get(
            "/", headers={"Authorization": f"Bearer {superuser.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert len(response_json) == 3
        for user in response_json:
            assert "id" in user
            assert "hashed_password" not in user


@pytest.mark.router
@pytest.mark.asyncio
class TestGetUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/000")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.get(
            "/000", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.get(
            "/000", headers={"Authorization": f"Bearer {superuser.id}"}
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
        assert data["id"] == user.id
        assert "hashed_password" not in data


@pytest.mark.router
@pytest.mark.asyncio
class TestUpdateUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.patch("/000")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.patch(
            "/000", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.patch(
            "/000", json={}, headers={"Authorization": f"Bearer {superuser.id}"}
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
        response = await test_app_client.delete("/000")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(self, test_app_client: httpx.AsyncClient, user: UserDB):
        response = await test_app_client.delete(
            "/000", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user(
        self, test_app_client: httpx.AsyncClient, superuser: UserDB
    ):
        response = await test_app_client.delete(
            "/000", headers={"Authorization": f"Bearer {superuser.id}"}
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
