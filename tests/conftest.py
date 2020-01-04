from typing import Any, List, Mapping, Optional, Tuple

import http.cookies
import pytest
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient

from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.password import get_password_hash

guinevere_password_hash = get_password_hash("guinevere")
angharad_password_hash = get_password_hash("angharad")
viviane_password_hash = get_password_hash("viviane")


class User(models.BaseUser):
    first_name: Optional[str]


class UserCreate(User, models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


@pytest.fixture
def user() -> UserDB:
    return UserDB(
        id="aaa",
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
    )


@pytest.fixture
def inactive_user() -> UserDB:
    return UserDB(
        id="bbb",
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
    )


@pytest.fixture
def superuser() -> UserDB:
    return UserDB(
        id="ccc",
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
    )


@pytest.fixture
def mock_user_db(user, inactive_user, superuser) -> BaseUserDatabase:
    class MockUserDatabase(BaseUserDatabase[UserDB]):
        async def list(self) -> List[UserDB]:
            return [user, inactive_user, superuser]

        async def get(self, id: str) -> Optional[UserDB]:
            if id == user.id:
                return user
            if id == inactive_user.id:
                return inactive_user
            if id == superuser.id:
                return superuser
            return None

        async def get_by_email(self, email: str) -> Optional[UserDB]:
            if email == user.email:
                return user
            if email == inactive_user.email:
                return inactive_user
            if email == superuser.email:
                return superuser
            return None

        async def create(self, user: UserDB) -> UserDB:
            return user

        async def update(self, user: UserDB) -> UserDB:
            return user

        async def delete(self, user: UserDB) -> None:
            pass

    return MockUserDatabase(UserDB)


class MockAuthentication(BaseAuthentication):
    def __init__(self, name: str = "mock"):
        super().__init__(name)
        self.scheme = OAuth2PasswordBearer("/users/login", auto_error=False)

    async def __call__(self, request: Request, user_db: BaseUserDatabase):
        token = await self.scheme.__call__(request)
        if token is not None:
            return await user_db.get(token)
        return None

    async def get_login_response(self, user: BaseUserDB, response: Response):
        return {"token": user.id}


@pytest.fixture
def mock_authentication():
    return MockAuthentication()


@pytest.fixture
def request_builder():
    def _request_builder(
        headers: Mapping[str, Any] = None, cookies: Mapping[str, str] = None
    ) -> Request:
        encoded_headers: List[Tuple[bytes, bytes]] = []

        if headers is not None:
            encoded_headers += [
                (key.lower().encode("latin-1"), headers[key].encode("latin-1"))
                for key in headers
            ]

        if cookies is not None:
            for key in cookies:
                cookie = http.cookies.SimpleCookie()  # type: http.cookies.BaseCookie
                cookie[key] = cookies[key]
                cookie_val = cookie.output(header="").strip()
                encoded_headers.append((b"cookie", cookie_val.encode("latin-1")))

        scope = {
            "type": "http",
            "headers": encoded_headers,
        }
        return Request(scope)

    return _request_builder


@pytest.fixture
def get_test_auth_client(mock_user_db):
    def _get_test_auth_client(backends: List[BaseAuthentication]) -> TestClient:
        app = FastAPI()
        authenticator = Authenticator(backends, mock_user_db)

        @app.get("/test-current-user")
        def test_current_user(user: UserDB = Depends(authenticator.get_current_user),):
            return user

        @app.get("/test-current-active-user")
        def test_current_active_user(
            user: UserDB = Depends(authenticator.get_current_active_user),
        ):
            return user

        @app.get("/test-current-superuser")
        def test_current_superuser(
            user: UserDB = Depends(authenticator.get_current_superuser),
        ):
            return user

        return TestClient(app)

    return _get_test_auth_client
