from typing import List, Optional

import pytest
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import Response
from starlette.testclient import TestClient

from fastapi_users.authentication import BaseAuthentication
from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.password import get_password_hash

guinevere_password_hash = get_password_hash("guinevere")
angharad_password_hash = get_password_hash("angharad")
viviane_password_hash = get_password_hash("viviane")


@pytest.fixture
def user() -> BaseUserDB:
    return BaseUserDB(
        id="aaa",
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
    )


@pytest.fixture
def inactive_user() -> BaseUserDB:
    return BaseUserDB(
        id="bbb",
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
    )


@pytest.fixture
def superuser() -> BaseUserDB:
    return BaseUserDB(
        id="ccc",
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
    )


@pytest.fixture
def mock_user_db(user, inactive_user, superuser) -> BaseUserDatabase:
    class MockUserDatabase(BaseUserDatabase):
        async def list(self) -> List[BaseUserDB]:
            return [user, inactive_user, superuser]

        async def get(self, id: str) -> Optional[BaseUserDB]:
            if id == user.id:
                return user
            if id == inactive_user.id:
                return inactive_user
            if id == superuser.id:
                return superuser
            return None

        async def get_by_email(self, email: str) -> Optional[BaseUserDB]:
            if email == user.email:
                return user
            if email == inactive_user.email:
                return inactive_user
            if email == superuser.email:
                return superuser
            return None

        async def create(self, user: BaseUserDB) -> BaseUserDB:
            return user

        async def update(self, user: BaseUserDB) -> BaseUserDB:
            return user

        async def delete(self, user: BaseUserDB) -> None:
            pass

    return MockUserDatabase()


@pytest.fixture
def mock_authentication():
    class MockAuthentication(BaseAuthentication):
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

        async def get_login_response(self, user: BaseUserDB, response: Response):
            return {"token": user.id}

        def get_current_user(self, user_db: BaseUserDatabase):
            async def _get_current_user(token: str = Depends(self.oauth2_scheme)):
                user = await self._get_authentication_method(user_db)(token)
                return self._get_current_user_base(user)

            return _get_current_user

        def get_current_active_user(self, user_db: BaseUserDatabase):
            async def _get_current_active_user(
                token: str = Depends(self.oauth2_scheme),
            ):
                user = await self._get_authentication_method(user_db)(token)
                return self._get_current_active_user_base(user)

            return _get_current_active_user

        def get_current_superuser(self, user_db: BaseUserDatabase):
            async def _get_current_superuser(token: str = Depends(self.oauth2_scheme)):
                user = await self._get_authentication_method(user_db)(token)
                return self._get_current_superuser_base(user)

            return _get_current_superuser

        def _get_authentication_method(self, user_db: BaseUserDatabase):
            async def authentication_method(token: str = Depends(self.oauth2_scheme)):
                return await user_db.get(token)

            return authentication_method

    return MockAuthentication()


@pytest.fixture
def get_test_auth_client(mock_user_db):
    def _get_test_auth_client(authentication):
        app = FastAPI()

        @app.get("/test-current-user")
        def test_current_user(
            user: BaseUserDB = Depends(authentication.get_current_user(mock_user_db)),
        ):
            return user

        @app.get("/test-current-active-user")
        def test_current_active_user(
            user: BaseUserDB = Depends(
                authentication.get_current_active_user(mock_user_db)
            ),
        ):
            return user

        @app.get("/test-current-superuser")
        def test_current_superuser(
            user: BaseUserDB = Depends(
                authentication.get_current_superuser(mock_user_db)
            ),
        ):
            return user

        return TestClient(app)

    return _get_test_auth_client
