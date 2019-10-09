from typing import List

from databases import Database
from sqlalchemy import Boolean, Column, String
from sqlalchemy.ext.declarative import declarative_base

from fastapi_users.db import BaseUserDatabase
from fastapi_users.models import UserDB

Base = declarative_base()


class BaseUser(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


users = BaseUser.__table__


class SQLAlchemyUserDatabase(BaseUserDatabase):

    database: Database

    def __init__(self, database):
        self.database = database

    async def list(self) -> List[UserDB]:
        query = users.select()
        return await self.database.fetch_all(query)

    async def get(self, id: str) -> UserDB:
        query = users.select().where(BaseUser.id == id)
        return await self.database.fetch_one(query)

    async def get_by_email(self, email: str) -> UserDB:
        query = users.select().where(BaseUser.email == email)
        return await self.database.fetch_one(query)

    async def create(self, user: UserDB) -> UserDB:
        query = users.insert().values(**user.dict())
        await self.database.execute(query)
        return user

    async def update(self, user: UserDB) -> UserDB:
        query = users.update().where(BaseUser.id == user.id).values(**user.dict())
        await self.database.execute(query)
        return user
