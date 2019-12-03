from typing import List, Optional, Type

from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import BaseUserDB


class BaseUserModel:
    id = fields.TextField(pk=True, generated=False)
    email = fields.CharField(index=True, unique=True, null=False, max_length=255)
    hashed_password = fields.CharField(null=False, max_length=255)
    is_active = fields.BooleanField(default=True, null=False)
    is_superuser = fields.BooleanField(default=False, null=False)

    class Meta:
        table = "user"


class TortoiseUserDatabase(BaseUserDatabase):

    model: Type[Model]

    def __init__(self, model: Type[Model]):
        self.model = model

    async def list(self) -> List[BaseUserDB]:
        users = await self.model.all()
        return [BaseUserDB.from_orm(user) for user in users]

    async def get(self, id: str) -> Optional[BaseUserDB]:
        try:
            user = await self.model.get(id=id)
            return BaseUserDB.from_orm(user)
        except DoesNotExist:
            return None

    async def get_by_email(self, email: str) -> Optional[BaseUserDB]:
        try:
            user = await self.model.get(email=email)
            return BaseUserDB.from_orm(user)
        except DoesNotExist:
            return None

    async def create(self, user: BaseUserDB) -> BaseUserDB:
        model = self.model(**user.dict())
        await model.save()
        return user

    async def update(self, user: BaseUserDB) -> BaseUserDB:
        user_dict = user.dict()
        user_dict.pop("id")  # Tortoise complains if we pass the PK again
        await self.model.filter(id=user.id).update(**user_dict)
        return user

    async def delete(self, user: BaseUserDB) -> None:
        await self.model.filter(id=user.id).delete()
