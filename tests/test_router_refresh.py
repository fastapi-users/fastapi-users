from datetime import datetime
from typing import AsyncGenerator, Callable, Optional, Tuple

import httpx
import pytest
from fastapi import FastAPI, status

from fastapi_users.authentication import Authenticator
from fastapi_users.router import get_auth_router, get_refresh_router
from fastapi_users.scopes import SystemScope
from tests.conftest import (
    MockBackend,
    UserModel,
    assert_valid_token_response,
    mock_token_data,
    mock_valid_access_token,
    mock_valid_refresh_token,
)


@pytest.fixture
def app_factory(
    mock_authentication_factory: Callable[[str], MockBackend], get_user_manager
):
    def _app_factory(requires_verification: bool) -> FastAPI:
        mock_authentication = mock_authentication_factory("mock")
        mock_authentication_bis = mock_authentication_factory("mock-bis")
        authenticator = Authenticator(
            [mock_authentication, mock_authentication_bis], get_user_manager
        )

        mock_auth_router = get_auth_router(
            mock_authentication,
            get_user_manager,
            authenticator,
            requires_verification=requires_verification,
        )
        mock_bis_auth_router = get_auth_router(
            mock_authentication_bis,
            get_user_manager,
            authenticator,
            requires_verification=requires_verification,
        )

        mock_refresh_router = get_refresh_router(
            mock_authentication,
            get_user_manager,
        )
        mock_bis_refresh_router = get_refresh_router(
            mock_authentication_bis,
            get_user_manager,
        )

        app = FastAPI()
        app.include_router(mock_auth_router, prefix="/mock")
        app.include_router(mock_bis_auth_router, prefix="/mock-bis")
        app.include_router(mock_refresh_router, prefix="/mock")
        app.include_router(mock_bis_refresh_router, prefix="/mock-bis")

        return app

    return _app_factory


@pytest.fixture(
    params=[True, False], ids=["required_verification", "not_required_verification"]
)
@pytest.mark.asyncio
async def test_app_client(
    request, get_test_client, app_factory
) -> AsyncGenerator[Tuple[httpx.AsyncClient, bool], None]:
    requires_verification = request.param
    app = app_factory(requires_verification)

    async for client in get_test_client(app):
        yield client, requires_verification


@pytest.mark.router
@pytest.mark.parametrize("refresh_token_enabled", [True], indirect=True)
@pytest.mark.parametrize("path", ["/mock", "/mock-bis"])
@pytest.mark.asyncio
class TestRefresh:
    async def test_malformed_token(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
    ):
        client, _ = test_app_client
        data = {"grant_type": "refresh_token", "refresh_token": "foo"}
        response = await client.post(f"{path}/refresh", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_access_token_used_as_refresh_token(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
        verified_user: UserModel,
    ):
        client, _ = test_app_client

        data = {
            "grant_type": "refresh_token",
            "refresh_token": mock_valid_access_token(verified_user),
        }
        response = await client.post(f"{path}/refresh", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "access_token_lifetime_seconds", [None, 3600], indirect=True
    )
    @pytest.mark.parametrize(
        "refresh_token_lifetime_seconds", [None, 86400], indirect=True
    )
    @pytest.mark.freeze_time("2022-09-01 09:00")
    async def test_valid_refresh_token(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
        verified_user: UserModel,
        freezer,
        access_token_lifetime_seconds: Optional[int],
        refresh_token_lifetime_seconds: Optional[int],
    ):
        print(f"test_valid_refresh_token: {access_token_lifetime_seconds}")
        client, _ = test_app_client

        data = {
            "grant_type": "refresh_token",
            "refresh_token": mock_valid_refresh_token(verified_user),
        }
        freezer.move_to("2022-09-01 10:00")
        response = await client.post(f"{path}/refresh", data=data)
        assert response.status_code == status.HTTP_200_OK
        expected_access_token = mock_token_data(
            user_id=verified_user.id,
            scopes={SystemScope.USER, SystemScope.VERIFIED},
            lifetime_seconds=access_token_lifetime_seconds,
            last_authenticated=datetime.fromisoformat("2022-09-01 09:00+00:00"),
        )
        expected_refresh_token = mock_token_data(
            user_id=verified_user.id,
            scopes={SystemScope.REFRESH},
            lifetime_seconds=refresh_token_lifetime_seconds,
            last_authenticated=datetime.fromisoformat("2022-09-01 09:00+00:00"),
        )
        assert_valid_token_response(
            response.json(),
            expected_access_token,
            expected_refresh_token,
        )


@pytest.mark.router
@pytest.mark.parametrize("refresh_token_enabled", [False], indirect=True)
@pytest.mark.parametrize("path", ["/mock", "/mock-bis"])
@pytest.mark.asyncio
class TestMisconfiguredRefresh:
    async def test_valid_refresh_token(
        self,
        path,
        test_app_client: Tuple[httpx.AsyncClient, bool],
        verified_user: UserModel,
    ):
        client, _ = test_app_client

        data = {
            "grant_type": "refresh_token",
            "refresh_token": mock_valid_refresh_token(verified_user),
        }
        response = await client.post(f"{path}/refresh", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "refresh_tokens_not_allowed"}
