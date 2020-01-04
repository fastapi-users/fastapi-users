from typing import List, Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD


class MongoDBUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for MongoDB.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param collection: Collection instance from `motor`.
    """

    collection: AsyncIOMotorCollection

    def __init__(self, user_db_model: Type[UD], collection: AsyncIOMotorCollection):
        super().__init__(user_db_model)
        self.collection = collection
        self.collection.create_index("id", unique=True)
        self.collection.create_index("email", unique=True)

    async def list(self) -> List[UD]:
        return [self.user_db_model(**user) async for user in self.collection.find()]

    async def get(self, id: str) -> Optional[UD]:
        user = await self.collection.find_one({"id": id})
        return self.user_db_model(**user) if user else None

    async def get_by_email(self, email: str) -> Optional[UD]:
        user = await self.collection.find_one({"email": email})
        return self.user_db_model(**user) if user else None

    async def create(self, user: UD) -> UD:
        await self.collection.insert_one(user.dict())
        return user

    async def update(self, user: UD) -> UD:
        await self.collection.replace_one({"id": user.id}, user.dict())
        return user

    async def delete(self, user: UD) -> None:
        await self.collection.delete_one({"id": user.id})
