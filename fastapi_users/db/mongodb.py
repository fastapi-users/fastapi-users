from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseUserDB


class MongoDBUserDatabase(BaseUserDatabase):
    """
    Database adapter for MongoDB.

    :param collection: Collection instance from `motor`.
    """

    collection: AsyncIOMotorCollection

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
        self.collection.create_index("id", unique=True)
        self.collection.create_index("email", unique=True)

    async def list(self) -> List[BaseUserDB]:
        return [BaseUserDB(**user) async for user in self.collection.find()]

    async def get(self, id: str) -> Optional[BaseUserDB]:
        user = await self.collection.find_one({"id": id})
        return BaseUserDB(**user) if user else None

    async def get_by_email(self, email: str) -> Optional[BaseUserDB]:
        user = await self.collection.find_one({"email": email})
        return BaseUserDB(**user) if user else None

    async def create(self, user: BaseUserDB) -> BaseUserDB:
        await self.collection.insert_one(user.dict())
        return user

    async def update(self, user: BaseUserDB) -> BaseUserDB:
        await self.collection.replace_one({"id": user.id}, user.dict())
        return user
