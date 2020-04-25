import pytest
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users.db import BaseUserDatabase
from tests.conftest import UserDB


@pytest.fixture
def create_oauth2_password_request_form():
    def _create_oauth2_password_request_form(username, password):
        return OAuth2PasswordRequestForm(username=username, password=password, scope="")

    return _create_oauth2_password_request_form


@pytest.mark.asyncio
@pytest.mark.db
async def test_not_implemented_methods(user):
    base_user_db = BaseUserDatabase(UserDB)

    with pytest.raises(NotImplementedError):
        await base_user_db.get("aaa")

    with pytest.raises(NotImplementedError):
        await base_user_db.get_by_email("lancelot@camelot.bt")

    with pytest.raises(NotImplementedError):
        await base_user_db.get_by_oauth_account("google", "user_oauth1")

    with pytest.raises(NotImplementedError):
        await base_user_db.create(user)

    with pytest.raises(NotImplementedError):
        await base_user_db.update(user)

    with pytest.raises(NotImplementedError):
        await base_user_db.delete(user)


@pytest.mark.db
class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_unknown_user(
        self, create_oauth2_password_request_form, mock_user_db
    ):
        form = create_oauth2_password_request_form("lancelot@camelot.bt", "guinevere")
        user = await mock_user_db.authenticate(form)
        assert user is None

    @pytest.mark.asyncio
    async def test_wrong_password(
        self, create_oauth2_password_request_form, mock_user_db
    ):
        form = create_oauth2_password_request_form("king.arthur@camelot.bt", "percival")
        user = await mock_user_db.authenticate(form)
        assert user is None

    @pytest.mark.asyncio
    async def test_valid_credentials(
        self, create_oauth2_password_request_form, mock_user_db
    ):
        form = create_oauth2_password_request_form(
            "king.arthur@camelot.bt", "guinevere"
        )
        user = await mock_user_db.authenticate(form)
        assert user is not None
        assert user.email == "king.arthur@camelot.bt"

    @pytest.mark.asyncio
    async def test_upgrade_password_hash(
        self, mocker, create_oauth2_password_request_form, mock_user_db
    ):
        verify_and_update_password_patch = mocker.patch(
            "fastapi_users.password.verify_and_update_password"
        )
        verify_and_update_password_patch.return_value = (True, "updated_hash")
        mocker.spy(mock_user_db, "update")

        form = create_oauth2_password_request_form(
            "king.arthur@camelot.bt", "guinevere"
        )
        user = await mock_user_db.authenticate(form)
        assert user is not None
        assert user.email == "king.arthur@camelot.bt"
        assert mock_user_db.update.called is True
