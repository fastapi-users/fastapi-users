from typing import List

from databases import Database
from sqlalchemy import Boolean, Column, String, Table

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import UserDB


class BaseUser:
    __tablename__ = "user"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


class SQLAlchemyUserDatabase(BaseUserDatabase):

    database: Database
    users: Table

    def __init__(self, database: Database, users: Table):
        self.database = database
        self.users = users

    async def list(self) -> List[UserDB]:
        query = self.users.select()
        return await self.database.fetch_all(query)

    async def get(self, id: str) -> UserDB:
        query = self.users.select().where(self.users.c.id == id)
        return await self.database.fetch_one(query)

    async def get_by_email(self, email: str) -> UserDB:
        query = self.users.select().where(self.users.c.email == email)
        return await self.database.fetch_one(query)

    async def create(self, user: UserDB) -> UserDB:
        query = self.users.insert().values(**user.dict())
        await self.database.execute(query)
        return user

    async def update(self, user: UserDB) -> UserDB:
        query = (
            self.users.update().where(self.users.c.id == user.id).values(**user.dict())
        )
        await self.database.execute(query)
        return user
