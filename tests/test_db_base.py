import pytest
from fastapi.security import OAuth2PasswordRequestForm


@pytest.fixture
def create_oauth2_password_request_form():
    def _create_oauth2_password_request_form(username, password):
        return OAuth2PasswordRequestForm(
            username=username,
            password=password,
            scope='',
        )
    return _create_oauth2_password_request_form


class TestAuthenticate:

    @pytest.mark.asyncio
    async def test_unknown_user(self, create_oauth2_password_request_form, mock_user_db):
        form = create_oauth2_password_request_form('lancelot@camelot.bt', 'guinevere')
        user = await mock_user_db.authenticate(form)
        assert user is None

    @pytest.mark.asyncio
    async def test_wrong_password(self, create_oauth2_password_request_form, mock_user_db):
        form = create_oauth2_password_request_form('king.arthur@camelot.bt', 'percival')
        user = await mock_user_db.authenticate(form)
        assert user is None

    @pytest.mark.asyncio
    async def test_valid_credentials(self, create_oauth2_password_request_form, mock_user_db):
        form = create_oauth2_password_request_form('king.arthur@camelot.bt', 'guinevere')
        user = await mock_user_db.authenticate(form)
        assert user is not None
        assert user.email == 'king.arthur@camelot.bt'
