from typing import AsyncGenerator

import httpx
import pytest
from fastapi import Depends, FastAPI, status

from fastapi_users import FastAPIUsers
from tests.conftest import IDType, User, UserCreate, UserModel, UserUpdate


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    secret,
    get_user_manager,
    mock_authentication,
    oauth_client,
    get_test_client,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    fastapi_users = FastAPIUsers[UserModel, IDType](
        get_user_manager, [mock_authentication]
    )

    app = FastAPI()
    app.include_router(fastapi_users.get_register_router(User, UserCreate))
    app.include_router(fastapi_users.get_reset_password_router())
    app.include_router(fastapi_users.get_auth_router(mock_authentication))
    app.include_router(
        fastapi_users.get_oauth_router(oauth_client, mock_authentication, secret)
    )

    @app.delete("/users/me")
    def custom_users_route():
        return None

    app.include_router(
        fastapi_users.get_users_router(User, UserUpdate), prefix="/users"
    )
    app.include_router(fastapi_users.get_verify_router(User))

    @app.get("/current-user", response_model=User)
    def current_user(user: UserModel = Depends(fastapi_users.current_user())):
        return user

    @app.get("/current-active-user", response_model=User)
    def current_active_user(
        user: UserModel = Depends(fastapi_users.current_user(active=True)),
    ):
        return user

    @app.get("/current-verified-user", response_model=User)
    def current_verified_user(
        user: UserModel = Depends(fastapi_users.current_user(verified=True)),
    ):
        return user

    @app.get("/current-superuser", response_model=User)
    def current_superuser(
        user: UserModel = Depends(
            fastapi_users.current_user(active=True, superuser=True)
        )
    ):
        return user

    @app.get("/current-verified-superuser", response_model=User)
    def current_verified_superuser(
        user: UserModel = Depends(
            fastapi_users.current_user(active=True, verified=True, superuser=True)
        ),
    ):
        return user

    @app.get("/optional-current-user", response_model=User)
    def optional_current_user(
        user: UserModel = Depends(fastapi_users.current_user(optional=True)),
    ):
        return user

    @app.get("/optional-current-active-user", response_model=User)
    def optional_current_active_user(
        user: UserModel = Depends(
            fastapi_users.current_user(optional=True, active=True)
        ),
    ):
        return user

    @app.get("/optional-current-verified-user", response_model=User)
    def optional_current_verified_user(
        user: UserModel = Depends(
            fastapi_users.current_user(optional=True, verified=True)
        ),
    ):
        return user

    @app.get("/optional-current-superuser", response_model=User)
    def optional_current_superuser(
        user: UserModel = Depends(
            fastapi_users.current_user(optional=True, active=True, superuser=True)
        ),
    ):
        return user

    @app.get("/optional-current-verified-superuser", response_model=User)
    def optional_current_verified_superuser(
        user: UserModel = Depends(
            fastapi_users.current_user(
                optional=True, active=True, verified=True, superuser=True
            )
        ),
    ):
        return user

    async for client in get_test_client(app):
        yield client


@pytest.mark.fastapi_users
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,method",
    [
        ("/register", "POST"),
        ("/request-verify-token", "POST"),
        ("/verify", "POST"),
        ("/forgot-password", "POST"),
        ("/reset-password", "POST"),
        ("/login", "POST"),
        ("/logout", "POST"),
        ("/register", "POST"),
        ("/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f", "GET"),
        ("/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f", "PATCH"),
        ("/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f", "DELETE"),
    ],
)
async def test_route_exists(test_app_client: httpx.AsyncClient, path: str, method: str):
    response = await test_app_client.request(method, path)
    assert response.status_code not in (
        status.HTTP_404_NOT_FOUND,
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@pytest.mark.fastapi_users
@pytest.mark.asyncio
async def test_custom_users_route_not_catched(test_app_client: httpx.AsyncClient):
    response = await test_app_client.request("DELETE", "/users/me")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/current-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentActiveUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-active-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-active-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserModel
    ):
        response = await test_app_client.get(
            "/current-active-user",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/current-active-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentVerifiedUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-verified-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-verified-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token_unverified_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/current-verified-user",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_valid_token_verified_user(
        self, test_app_client: httpx.AsyncClient, verified_user: UserModel
    ):
        response = await test_app_client.get(
            "/current-verified-user",
            headers={"Authorization": f"Bearer {verified_user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentSuperuser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-superuser")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_valid_token_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": f"Bearer {superuser.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentVerifiedSuperuser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-verified-superuser")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-verified-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/current-verified-superuser",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_valid_token_verified_user(
        self, test_app_client: httpx.AsyncClient, verified_user: UserModel
    ):
        response = await test_app_client.get(
            "/current-verified-superuser",
            headers={"Authorization": f"Bearer {verified_user.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_valid_token_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        response = await test_app_client.get(
            "/current-verified-superuser",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_valid_token_verified_superuser(
        self, test_app_client: httpx.AsyncClient, verified_superuser: UserModel
    ):
        response = await test_app_client.get(
            "/current-verified-superuser",
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-user")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentVerifiedUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-verified-user")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-verified-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_unverified_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-verified-user",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_verified_user(
        self, test_app_client: httpx.AsyncClient, verified_user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-verified-user",
            headers={"Authorization": f"Bearer {verified_user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentActiveUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-active-user")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-active-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-active-user",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-active-user",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentSuperuser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-superuser")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-superuser",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-superuser",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentVerifiedSuperuser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-verified-superuser")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-verified-superuser",
            headers={"Authorization": "Bearer foo"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-verified-superuser",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_verified_user(
        self, test_app_client: httpx.AsyncClient, verified_user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-verified-superuser",
            headers={"Authorization": f"Bearer {verified_user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-verified-superuser",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_verified_superuser(
        self, test_app_client: httpx.AsyncClient, verified_superuser: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-verified-superuser",
            headers={"Authorization": f"Bearer {verified_superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None
