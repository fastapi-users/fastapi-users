import httpx

from conftest import TEST_USER_EMAIL


async def test_me_authorized(jwt_authorized_async_client: httpx.AsyncClient):
    response = await jwt_authorized_async_client.get('/users/me')
    assert response.status_code == 200

    data = response.json()
    assert data['email'] == TEST_USER_EMAIL


async def test_me_unauthorized(async_client: httpx.AsyncClient):
    response = await async_client.get('/users/me')
    assert response.status_code == 401


async def test_me_override_current_user(override_current_user_async_client: httpx.AsyncClient):
    response = await override_current_user_async_client.get('/authenticated-route')
    assert response.status_code == 200
    assert response.json()['message'] == f"Hello {TEST_USER_EMAIL}!"
