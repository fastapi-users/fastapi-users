import pytest
from fastapi import Depends, FastAPI
from starlette import status
from starlette.testclient import TestClient

from fastapi_users.models import BaseUserDB


@pytest.fixture
def test_auth_client(mock_authentication, mock_user_db):
    app = FastAPI()

    @app.get("/test-current-user")
    def test_current_user(
        user: BaseUserDB = Depends(mock_authentication.get_current_user(mock_user_db))
    ):
        return user

    @app.get("/test-current-active-user")
    def test_current_active_user(
        user: BaseUserDB = Depends(
            mock_authentication.get_current_active_user(mock_user_db)
        )
    ):
        return user

    @app.get("/test-current-superuser")
    def test_current_superuser(
        user: BaseUserDB = Depends(
            mock_authentication.get_current_superuser(mock_user_db)
        )
    ):
        return user

    return TestClient(app)


class TestGetCurrentUser:
    def test_missing_token(self, test_auth_client):
        response = test_auth_client.get("/test-current-user")
        print(response.json())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_auth_client):
        response = test_auth_client.get(
            "/test-current-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_inactive_user(self, test_auth_client, inactive_user):
        response = test_auth_client.get(
            "/test-current-user",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == inactive_user.id

    def test_valid_token(self, test_auth_client, user):
        response = test_auth_client.get(
            "/test-current-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == user.id


class TestGetCurrentActiveUser:
    def test_missing_token(self, test_auth_client):
        response = test_auth_client.get("/test-current-active-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_auth_client):
        response = test_auth_client.get(
            "/test-current-active-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_inactive_user(self, test_auth_client, inactive_user):
        response = test_auth_client.get(
            "/test-current-active-user",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token(self, test_auth_client, user):
        response = test_auth_client.get(
            "/test-current-active-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == user.id


class TestGetCurrentSuperuser:
    def test_missing_token(self, test_auth_client):
        response = test_auth_client.get("/test-current-superuser")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_auth_client):
        response = test_auth_client.get(
            "/test-current-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_inactive_user(self, test_auth_client, inactive_user):
        response = test_auth_client.get(
            "/test-current-superuser",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_regular_user(self, test_auth_client, user):
        response = test_auth_client.get(
            "/test-current-superuser", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_valid_token_superuser(self, test_auth_client, superuser):
        response = test_auth_client.get(
            "/test-current-superuser",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["id"] == superuser.id
