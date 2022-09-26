import json
from datetime import datetime

import pytest

from fastapi_users.authentication.token import TokenData, UserTokenData
from tests.conftest import IDType, UserManager, UserModel


@pytest.mark.authentication
def test_token_to_json(token_data: UserTokenData[UserModel, IDType]):

    token = token_data.json()

    decoded = json.loads(token)

    assert decoded["user_id"] == str(token_data.user.id)
    assert set(decoded["scopes"]) == token_data.scopes

    assert datetime.fromisoformat(decoded["created_at"]) == token_data.created_at

    assert (
        datetime.fromisoformat(decoded["last_authenticated"])
        == token_data.last_authenticated
    )

    if token_data.expires_at:
        assert "expires_at" in decoded
        assert datetime.fromisoformat(decoded["expires_at"]) == token_data.expires_at


@pytest.mark.authentication
@pytest.mark.asyncio
async def test_token_from_json(
    token_data: UserTokenData[UserModel, IDType], user_manager: UserManager
):

    token_data_dict = {
        "user_id": str(token_data.user.id),
        "created_at": token_data.created_at.isoformat(),
        "last_authenticated": token_data.last_authenticated.isoformat(),
        "scopes": list(token_data.scopes),
    }
    if token_data.expires_at:
        token_data_dict["expires_at"] = token_data.expires_at.isoformat()

    token = json.dumps(token_data_dict)

    parsed_token = TokenData.parse_raw(token)
    parsed_user_token = await parsed_token.lookup_user(user_manager)

    assert parsed_user_token == token_data
