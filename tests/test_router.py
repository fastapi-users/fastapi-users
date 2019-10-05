from starlette import status
from starlette.testclient import TestClient
import pytest


@pytest.fixture
def test_app_client() -> TestClient:
    from fastapi import FastAPI
    from fastapi_users.router import router

    app = FastAPI()
    app.include_router(router)

    return TestClient(app)


def test_register_empty_body(test_app_client: TestClient):
    response = test_app_client.post('/register', json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_missing_password(test_app_client: TestClient):
    json = {
        'email': 'king.arthur@camelot.bt',
    }
    response = test_app_client.post('/register', json=json)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_wrong_email(test_app_client: TestClient):
    json = {
        'email': 'king.arthur',
        'password': 'guinevere',
    }
    response = test_app_client.post('/register', json=json)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_valid_body(test_app_client: TestClient):
    json = {
        'email': 'king.arthur@camelot.bt',
        'password': 'guinevere',
    }
    response = test_app_client.post('/register', json=json)
    assert response.status_code == status.HTTP_200_OK
