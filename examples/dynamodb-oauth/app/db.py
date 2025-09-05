from aiopynamodb.models import Model

from fastapi_users.db import (
    DynamoDBBaseOAuthAccountTableUUID,
    DynamoDBBaseUserTableUUID,
    DynamoDBUserDatabase,
)


class Base(Model):
    pass


class OAuthAccount(DynamoDBBaseOAuthAccountTableUUID, Base):
    pass


class User(DynamoDBBaseUserTableUUID, Base):
    oauth_accounts: list[OAuthAccount] = []


async def get_user_db():
    yield DynamoDBUserDatabase(User, OAuthAccount)
