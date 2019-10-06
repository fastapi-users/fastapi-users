import pytest
from starlette import status
from starlette.testclient import TestClient


@pytest.fixture
def test_app_client(mock_db_interface) -> TestClient:
    from fastapi import FastAPI
    from fastapi_users.router import UserRouter

    userRouter = UserRouter(mock_db_interface)

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


class TestLogin:

    def test_empty_body(self, test_app_client: TestClient):
        response = test_app_client.post('/login', json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_email(self, test_app_client: TestClient):
        json = {
            'password': 'guinevere',
        }
        response = test_app_client.post('/login', json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_password(self, test_app_client: TestClient):
        json = {
            'email': 'king.arthur@camelot.bt',
        }
        response = test_app_client.post('/login', json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_not_existing_user(self, test_app_client: TestClient):
        json = {
            'email': 'lancelot@camelot.bt',
            'password': 'guinevere',
        }
        response = test_app_client.post('/login', json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_wrong_password(self, test_app_client: TestClient):
        json = {
            'email': 'king.arthur@camelot.bt',
            'password': 'percival',
        }
        response = test_app_client.post('/login', json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_valid_credentials(self, test_app_client: TestClient):
        json = {
            'email': 'king.arthur@camelot.bt',
            'password': 'guinevere',
        }
        response = test_app_client.post('/login', json=json)
        assert response.status_code == status.HTTP_200_OK
