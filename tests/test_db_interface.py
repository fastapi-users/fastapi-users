import pytest

from fastapi_users.models import UserLogin


class TestAuthenticate:

    @pytest.mark.asyncio
    async def test_unknown_user(self, mock_db_interface):
        user = await mock_db_interface.authenticate(UserLogin(
            email='lancelot@camelot.bt',
            password='guinevere',
        ))
        assert user is None

    @pytest.mark.asyncio
    async def test_wrong_password(self, mock_db_interface):
        user = await mock_db_interface.authenticate(UserLogin(
            email='king.arthur@camelot.bt',
            password='percival',
        ))
        assert user is None

    @pytest.mark.asyncio
    async def test_valid_credentials(self, mock_db_interface):
        user = await mock_db_interface.authenticate(UserLogin(
            email='king.arthur@camelot.bt',
            password='guinevere',
        ))
        assert user is not None
        assert user.email == 'king.arthur@camelot.bt'
