from typing import List, Optional, Type

from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB


class BaseUserModel:
    id: str = fields.TextField(pk=True, generated=False)
    email: str = fields.CharField(index=True, unique=True, null=False, max_length=255)
    hashed_password: str = fields.CharField(null=False, max_length=255)
    is_active: bool = fields.BooleanField(default=True, null=False)
    is_superuser: bool = fields.BooleanField(default=False, null=False)

    class Meta:
        table = "user"


class TortoiseUserDatabase(BaseUserDatabase):
    def __init__(self, user_model: Type[Model]):
        self._model = user_model

    async def list(self) -> List[BaseUserDB]:
        users = await self._model.all()
        return [BaseUserDB.from_orm(user) for user in users]

    async def get(self, id: str) -> Optional[BaseUserDB]:
        try:
            user = await self._model.filter(id=id).first()
        except DoesNotExist:
            user = None
        return BaseUserDB.from_orm(user) if user else None

    async def get_by_email(self, email: str) -> Optional[BaseUserDB]:
        try:
            user = await self._model.filter(email=email).first()
        except DoesNotExist:
            user = None
        return BaseUserDB.from_orm(user) if user else None

    async def create(self, user: BaseUserDB) -> BaseUserDB:
        model = self._model(**user.dict())
        await model.save()
        return user

    async def update(self, user: BaseUserDB) -> BaseUserDB:
        usr = user.create_update_dict_superuser()
        await self._model.filter(id=user.id).update(**usr)
        return user

    async def delete(self, user: BaseUserDB) -> None:
        await self._model.filter(id=user.id).delete()
