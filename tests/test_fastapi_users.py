import pytest
from fastapi import Depends, FastAPI
from starlette import status
from starlette.testclient import TestClient

from fastapi_users import FastAPIUsers
from fastapi_users.models import BaseUser, BaseUserDB


@pytest.fixture
def fastapi_users(mock_user_db, mock_authentication) -> FastAPIUsers:
    class User(BaseUser):
        pass

    return FastAPIUsers(mock_user_db, mock_authentication, User)


@pytest.fixture
def test_app_client(fastapi_users: FastAPIUsers) -> TestClient:
    app = FastAPI()
    app.include_router(fastapi_users.router)

    @app.get("/authenticated")
    def authenticated(user=Depends(fastapi_users.get_current_user)):
        return user

    return TestClient(app)


class TestRouter:
    def test_routes_exist(self, test_app_client: TestClient):
        response = test_app_client.post("/register")
        assert response.status_code != status.HTTP_404_NOT_FOUND

        response = test_app_client.post("/login")
        assert response.status_code != status.HTTP_404_NOT_FOUND


class TestGetCurrentUser:
    def test_missing_token(self, test_app_client: TestClient):
        response = test_app_client.get("/authenticated")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_app_client: TestClient):
        response = test_app_client.get(
            "/authenticated", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token(self, test_app_client: TestClient, user: BaseUserDB):
        response = test_app_client.get(
            "/authenticated", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
