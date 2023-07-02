import httpx

from conftest import TEST_USER_EMAIL


async def test_register(jwt_authorized_async_client: httpx.AsyncClient):
    response = await jwt_authorized_async_client.get('/users/me')
    assert response.status_code == 200

    data = response.json()
    assert data['email'] == TEST_USER_EMAIL
