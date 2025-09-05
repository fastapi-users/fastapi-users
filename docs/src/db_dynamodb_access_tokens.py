from aiopynamodb.models import Model
from fastapi_users_db_dynamodb.access_token import (
    DynamoDBAccessTokenDatabase,
    DynamoDBBaseAccessTokenTableUUID,
)

from fastapi_users.db import DynamoDBBaseUserTableUUID, DynamoDBUserDatabase


class Base(Model):
    pass


class User(DynamoDBBaseUserTableUUID, Base):
    pass


class AccessToken(DynamoDBBaseAccessTokenTableUUID, Base):  # (1)!
    pass


async def get_user_db():
    yield DynamoDBUserDatabase(User)


async def get_access_token_db():  # (2)!
    yield DynamoDBAccessTokenDatabase(AccessToken)
    yield DynamoDBAccessTokenDatabase(AccessToken)
