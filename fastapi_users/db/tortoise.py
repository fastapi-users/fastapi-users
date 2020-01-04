from typing import List, Optional, Type

from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD


class TortoiseBaseUserModel(Model):
    id = fields.CharField(pk=True, generated=False, max_length=255)
    email = fields.CharField(index=True, unique=True, null=False, max_length=255)
    hashed_password = fields.CharField(null=False, max_length=255)
    is_active = fields.BooleanField(default=True, null=False)
    is_superuser = fields.BooleanField(default=False, null=False)

    class Meta:
        abstract = True


class TortoiseUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for Tortoise ORM.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param model: Tortoise ORM model.
    """

    model: Type[TortoiseBaseUserModel]

    def __init__(self, user_db_model: Type[UD], model: Type[TortoiseBaseUserModel]):
        super().__init__(user_db_model)
        self.model = model

    async def list(self) -> List[UD]:
        users = await self.model.all()
        return [self.user_db_model.from_orm(user) for user in users]

    async def get(self, id: str) -> Optional[UD]:
        try:
            user = await self.model.get(id=id)
            return self.user_db_model.from_orm(user)
        except DoesNotExist:
            return None

    async def get_by_email(self, email: str) -> Optional[UD]:
        try:
            user = await self.model.get(email=email)
            return self.user_db_model.from_orm(user)
        except DoesNotExist:
            return None

    async def create(self, user: UD) -> UD:
        model = self.model(**user.dict())
        await model.save()
        return user

    async def update(self, user: UD) -> UD:
        user_dict = user.dict()
        user_dict.pop("id")  # Tortoise complains if we pass the PK again
        await self.model.filter(id=user.id).update(**user_dict)
        return user

    async def delete(self, user: UD) -> None:
        await self.model.filter(id=user.id).delete()
