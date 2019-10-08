import pytest
from fastapi import FastAPI
from starlette import status
from starlette.testclient import TestClient

from fastapi_users.models import UserDB
from fastapi_users.router import UserRouter


@pytest.fixture
def test_app_client(mock_user_db, mock_authentication) -> TestClient:
    userRouter = UserRouter(mock_user_db, mock_authentication)

    app = FastAPI()
    app.include_router(userRouter)

    return TestClient(app)


class TestRegister:

    def test_empty_body(self, test_app_client: TestClient):
        response = test_app_client.post('/register', json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_password(self, test_app_client: TestClient):
        json = {
            'email': 'king.arthur@camelot.bt',
        }
        response = test_app_client.post('/register', json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_wrong_email(self, test_app_client: TestClient):
        json = {
            'email': 'king.arthur',
            'password': 'guinevere',
        }
        response = test_app_client.post('/register', json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_valid_body(self, test_app_client: TestClient):
        json = {
            'email': 'king.arthur@camelot.bt',
            'password': 'guinevere',
        }
        response = test_app_client.post('/register', json=json)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert 'hashed_password' not in response_json
        assert 'password' not in response_json
        assert 'id' in response_json


class TestLogin:

    def test_empty_body(self, test_app_client: TestClient):
        response = test_app_client.post('/login', data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_username(self, test_app_client: TestClient):
        data = {
            'password': 'guinevere',
        }
        response = test_app_client.post('/login', data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_password(self, test_app_client: TestClient):
        data = {
            'username': 'king.arthur@camelot.bt',
        }
        response = test_app_client.post('/login', data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_not_existing_user(self, test_app_client: TestClient):
        data = {
            'username': 'lancelot@camelot.bt',
            'password': 'guinevere',
        }
        response = test_app_client.post('/login', data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_wrong_password(self, test_app_client: TestClient):
        data = {
            'username': 'king.arthur@camelot.bt',
            'password': 'percival',
        }
        response = test_app_client.post('/login', data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_valid_credentials(self, test_app_client: TestClient, user: UserDB):
        data = {
            'username': 'king.arthur@camelot.bt',
            'password': 'guinevere',
        }
        response = test_app_client.post('/login', data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'token': user.id}

    def test_inactive_user(self, test_app_client: TestClient):
        data = {
            'username': 'percival@camelot.bt',
            'password': 'angharad',
        }
        response = test_app_client.post('/login', data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
