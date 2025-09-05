from aiopynamodb.models import Model

from fastapi_users.db import DynamoDBBaseUserTableUUID, DynamoDBUserDatabase


class Base(Model):
    pass


class User(DynamoDBBaseUserTableUUID, Base):
    pass


async def get_user_db():
    yield DynamoDBUserDatabase(User)
