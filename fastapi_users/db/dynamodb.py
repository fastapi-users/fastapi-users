import json
from typing import Mapping, Optional, Type

import aioboto3
from boto3.dynamodb.conditions import Key
from pydantic import UUID4

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD


class NotSetOAuthAccountTableError(Exception):
    """
    OAuth table was not set in DB adapter but was needed.

    Raised when trying to create/update a user with OAuth accounts set
    but no table were specified in the DB adapter.
    """

    pass


class DynamoDBUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for AWS DynamoDB.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param collection: Collection instance from `motor`.
    """

    def __init__(
        self,
        user_db_model: Type[UD],
        resource_args: Mapping,
        users_table: str,
        users_email_index: str,
        oauth_accounts_table: Optional[str] = None,
        oauth_accounts_user_index: Optional[str] = None,
        oauth_accounts_account_index: Optional[str] = None
    ):
        super().__init__(user_db_model)
        self.resource_args = resource_args
        self.users_table = users_table
        self.users_email_index = users_email_index
        self.oauth_accounts_table = oauth_accounts_table

        if self.oauth_accounts_table and not (oauth_accounts_user_index and oauth_accounts_account_index):
            raise ValueError("index names must be provided for oauth accounts table")
        self.oauth_user_index = oauth_accounts_user_index
        self.oauth_account_index = oauth_accounts_account_index

    async def get(self, id: UUID4) -> Optional[UD]:
        async with aioboto3.resource("dynamodb", **self.resource_args) as db:
            table = await db.Table(self.users_table)
            response = await table.get_item(Key={"id": str(id)})
            user = response.get("Item")
            return await self._make_user(user) if user else None

    async def get_by_email(self, email: str) -> Optional[UD]:
        async with aioboto3.resource("dynamodb", **self.resource_args) as db:
            table = await db.Table(self.users_table)
            response = await table.query(
                IndexName=self.users_email_index,
                KeyConditionExpression=Key("email").eq(email)
            )
            results = response.get("Items")
            user = results[0] if results else None
        return await self._make_user(user) if user else None

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UD]:
        if self.oauth_accounts_table:
            async with aioboto3.resource("dynamodb", **self.resource_args) as db:
                table = await db.Table(self.oauth_accounts_table)
                response = await table.query(
                    IndexName=self.oauth_account_index,
                    KeyConditionExpression=Key("oauth_name").eq(oauth) & Key("account_id").eq(account_id)
                )
                results = response.get("Items")
                if results:
                    oauth_account = results[0]
                    user = await self.get(oauth_account.user_id)
                    return await self._make_user(user.dict()) if user else None
        raise NotSetOAuthAccountTableError()

    async def create(self, user: UD) -> UD:
        user_dict = json.loads(user.json())
        oauth_accounts_values = None

        if "oauth_accounts" in user_dict:
            oauth_accounts_values = []

            oauth_accounts = user_dict.pop("oauth_accounts")
            for oauth_account in oauth_accounts:
                oauth_accounts_values.append({"user_id": user_dict["id"], **oauth_account})

        async with aioboto3.resource("dynamodb", **self.resource_args) as db:
            table = await db.Table(self.users_table)
            await table.put_item(Item=user_dict)

            if oauth_accounts_values is not None:
                if self.oauth_accounts_table is None:
                    raise NotSetOAuthAccountTableError()
                table = await db.Table(self.oauth_accounts_table)
                async with table.batch_writer() as batch:
                    for oauth_account in oauth_accounts_values:
                        await batch.put_item(Item=oauth_account)

        return user

    async def update(self, user: UD) -> UD:
        user_dict = json.loads(user.json())

        async with aioboto3.resource("dynamodb", **self.resource_args) as db:
            if "oauth_accounts" in user_dict:
                if self.oauth_accounts_table is None:
                    raise NotSetOAuthAccountTableError()

                table = await db.Table(self.oauth_accounts_table)
                response = await table.query(
                    IndexName=self.oauth_user_index,
                    KeyConditionExpression=Key("user_id").eq(user_dict["id"])
                )
                old_oauth_accounts = response.get("Items")

                oauth_accounts_values = []
                new_oauth_accounts = user_dict.pop("oauth_accounts")
                for oauth_account in new_oauth_accounts:
                    oauth_accounts_values.append({"user_id": user_dict["id"], **oauth_account})

                async with table.batch_writer() as batch:
                    for oauth_account in old_oauth_accounts:
                        await batch.delete_item(Key=oauth_account.id)
                    for oauth_account in oauth_accounts_values:
                        await batch.put_item(Item=oauth_account)

            table = await db.Table(self.users_table)
            await table.put_item(Item=user_dict)

        return user

    async def delete(self, user: UD) -> None:
        user_dict = json.loads(user.json())
        async with aioboto3.resource("dynamodb", **self.resource_args) as db:
            table = await db.Table(self.users_table)
            await table.delete_item(Key={"id": user_dict["id"]})

    async def _make_user(self, user: Mapping) -> UD:
        user_dict = {**user}

        if self.oauth_accounts_table:
            async with aioboto3.resource("dynamodb", **self.resource_args) as db:
                table = await db.Table(self.oauth_accounts_table)
                response = await table.query(
                    IndexName=self.oauth_user_index,
                    KeyConditionExpression=Key("user_id").eq(user["id"])
                )
                oauth_accounts = response.get('Items')
                user_dict["oauth_accounts"] = oauth_accounts

        return self.user_db_model(**user_dict)
