from typing import List, Type, Optional

from fastapi_users.db import BaseUserDatabase
from tortoise import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist

from fastapi_users.models import BaseUserDB


class BaseUserModel(Model):
    id: int = fields.IntField(pk=True)
    email: str = fields.TextField(index=True, unique=True, null=False)
    hashed_password: str = fields.TextField(null=False)
    is_active: bool = fields.BooleanField(default=True, null=False)
    is_superuser: bool = fields.BooleanField(default=False, null=False)

    class Meta:
        table = "user"

class TortoiseUserDatabase(BaseUserDatabase):

    def __init__(self, user_model: Type[BaseUserModel]):
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
        await self._model.create(**user.dict())
        return user

    async def update(self, user: BaseUserDB) -> BaseUserDB:
        await self._model.filter(id=user.id).update(**user.dict())
        return user

    async def delete(self, user: BaseUserDB) -> None:
        await self._model.filter(id=user.id).delete()






