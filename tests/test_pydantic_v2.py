import pytest

from fastapi_users.schemas import BaseUser
from pydantic import BaseModel


@pytest.mark.asyncio
async def test_pydantic_v2(monkeypatch: pytest.MonkeyPatch):
    if hasattr(BaseModel, "dict"):
        # Swap the dict attribute for the new model_dump method
        BaseModel.model_dump = BaseModel.dict

        # Remove the old method
        monkeypatch.delattr(BaseModel, "dict")

        user = BaseUser(email="king.arthur@tintagel.bt")

        # Test CreateUpdateDictModel as if we were running Pydantic v2
        user.create_update_dict()
        user.create_update_dict_superuser()
