import jwt
import pytest
from fastapi import Depends, FastAPI
from starlette import status
from starlette.responses import Response
from starlette.testclient import TestClient

from fastapi_users.authentication.jwt import JWTAuthentication, generate_jwt
from fastapi_users.models import UserDB

SECRET = 'SECRET'
ALGORITHM = 'HS256'
LIFETIME = 3600


@pytest.fixture
def jwt_authentication(mock_user_db):
    return JWTAuthentication(SECRET, LIFETIME, mock_user_db)


@pytest.fixture
def token():
    def _token(user, lifetime=LIFETIME):
        data = {'user_id': user.id}
        return generate_jwt(data, lifetime, SECRET, ALGORITHM)
    return _token


@pytest.fixture
def test_auth_client(jwt_authentication):
    app = FastAPI()

    @app.get('/test-auth')
    def test_auth(user: UserDB = Depends(jwt_authentication.get_authentication_method())):
        return user

    return TestClient(app)


@pytest.mark.asyncio
async def test_get_login_response(jwt_authentication, user):
    login_response = await jwt_authentication.get_login_response(user, Response())

    assert 'token' in login_response

    token = login_response['token']
    decoded = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    assert decoded['user_id'] == user.id


class TestGetAuthenticationMethod:

    def test_missing_token(self, test_auth_client):
        response = test_auth_client.get('/test-auth')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, test_auth_client):
        response = test_auth_client.get('/test-auth', headers={'Authorization': 'Bearer foo'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token_inactive_user(self, test_auth_client, token, inactive_user):
        response = test_auth_client.get('/test-auth', headers={'Authorization': f'Bearer {token(inactive_user)}'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_token(self, test_auth_client, token, user):
        response = test_auth_client.get('/test-auth', headers={'Authorization': f'Bearer {token(user)}'})
        assert response.status_code == status.HTTP_200_OK

        json = response.json()
        assert json['id'] == user.id
