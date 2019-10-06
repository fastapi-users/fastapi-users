import pytest
from starlette import status
from starlette.testclient import TestClient

from fastapi_users.db import UserDBInterface
from fastapi_users.models import UserDB


class MockUserDBInterface(UserDBInterface):

    async def create(self, user: UserDB) -> UserDB:
        return user


@pytest.fixture
def test_app_client() -> TestClient:
    from fastapi import FastAPI
    from fastapi_users.router import UserRouter

    userRouter = UserRouter(MockUserDBInterface())

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
