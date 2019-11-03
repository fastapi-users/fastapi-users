import pytest
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import Response

from fastapi_users.authentication import BaseAuthentication


@pytest.mark.asyncio
@pytest.mark.authentication
@pytest.mark.parametrize(
    "constructor_kwargs", [{}, {"scheme": OAuth2PasswordBearer(tokenUrl="/foo")}]
)
async def test_not_implemented_methods(constructor_kwargs, user, mock_user_db):
    response = Response()
    base_authentication = BaseAuthentication(**constructor_kwargs)

    with pytest.raises(NotImplementedError):
        await base_authentication.get_login_response(user, response)

    with pytest.raises(NotImplementedError):
        await base_authentication.get_current_user(mock_user_db)

    with pytest.raises(NotImplementedError):
        await base_authentication.get_current_active_user(mock_user_db)

    with pytest.raises(NotImplementedError):
        await base_authentication.get_current_superuser(mock_user_db)

    with pytest.raises(NotImplementedError):
        await base_authentication._get_authentication_method(mock_user_db)
