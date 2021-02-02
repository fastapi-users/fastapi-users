import datetime
from typing import Any, List, Optional, Type

import ormar
from ormar.exceptions import NoMatch
from pydantic import UUID4

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseOAuthAccount, UD


class OrmarBaseUserModel(ormar.Model):
    class Meta:
        tablename = "users"
        abstract = True

    # sqlalchemy adapter uses char(36) so for ormar it's string format
    id = ormar.UUID(primary_key=True, uuid_format="string")
    email = ormar.String(index=True, unique=True, nullable=False, max_length=255)
    hashed_password = ormar.String(nullable=False, max_length=255)
    is_active = ormar.Boolean(default=True, nullable=False)
    is_superuser = ormar.Boolean(default=False, nullable=False)
    is_verified = ormar.Boolean(default=False, nullable=False)


class OrmarBaseOAuthAccountModel(ormar.Model):
    class Meta:
        tablename = "oauth_accounts"
        abstract = True

    id = ormar.UUID(primary_key=True, uuid_format="string")
    oauth_name = ormar.String(nullable=False, max_length=255)
    access_token = ormar.String(nullable=False, max_length=255)
    expires_at = ormar.Integer(nullable=True)
    refresh_token = ormar.String(nullable=True, max_length=255)
    account_id = ormar.String(index=True, nullable=False, max_length=255)
    account_email = ormar.String(nullable=False, max_length=255)
    # added to keep ordering by creation_date
    created_date = ormar.DateTime(default=datetime.datetime.now)


class OrmarUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for ormar.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param model: ormar ORM model.
    :param oauth_account_model: Optional ormar ORM model of a OAuth account.
    """

    model: Type[OrmarBaseUserModel]
    oauth_account_model: Optional[Type[OrmarBaseOAuthAccountModel]]

    def __init__(
        self,
        user_db_model: Type[UD],
        model: Type[OrmarBaseUserModel],
        oauth_account_model: Optional[Type[OrmarBaseOAuthAccountModel]] = None,
    ):
        super().__init__(user_db_model)
        self.model = model
        self.oauth_account_model = oauth_account_model

    async def get_db_user(self, **kwargs: Any) -> Optional[ormar.Model]:
        try:
            query = self.model.objects.filter(**kwargs)
            if self.oauth_account_model is not None:
                # in ormar you can select from reverse too
                # only one query is run - faster execution
                query = query.select_related("oauth_accounts").order_by(
                    "oauth_accounts__created_date"
                )
            return await query.get()
        except NoMatch:
            return None

    async def get_user(self, **kwargs: Any) -> Optional[UD]:
        user = await self.get_db_user(**kwargs)
        return self.user_db_model(**user.dict()) if user else None

    async def create_oauth_models(
        self, model: ormar.Model, oauth_accounts: List[BaseOAuthAccount]
    ):
        # here we hardcore the name of the relation despite
        # that user can give a different one, yet it's the same as
        # in tortoise backend
        await self.oauth_account_model.objects.bulk_create(
            [
                self.oauth_account_model(user=model, **oacc.dict())
                for oacc in oauth_accounts
            ]
        )

    async def get(self, id: UUID4) -> Optional[UD]:
        return await self.get_user(id=id)

    async def get_by_email(self, email: str) -> Optional[UD]:
        return await self.get_user(email__iexact=email)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UD]:
        return await self.get_user(
            oauth_accounts__oauth_name=oauth, oauth_accounts__account_id=account_id
        )

    async def create(self, user: UD) -> UD:
        oauth_accounts = getattr(user, "oauth_accounts", [])
        model = await self.model(**user.dict(exclude={"oauth_accounts"})).save()
        if oauth_accounts and self.oauth_account_model:
            await self.create_oauth_models(model=model, oauth_accounts=oauth_accounts)
        return user

    async def update(self, user: UD) -> UD:
        oauth_accounts = getattr(user, "oauth_accounts", [])
        model = await self.get_db_user(id=user.id)
        # have no idea why other backends does not check if user exists?
        # is it some pattern that we have no exception at all?
        if not model:
            raise NoMatch("User with given id does not exist!")
        await model.update(**user.dict(exclude={"oauth_accounts"}))

        if oauth_accounts and self.oauth_account_model:
            # we issued query with select_related so we have oauths if they exist
            await model.oauth_accounts.clear(keep_reversed=False)
            await self.create_oauth_models(model=model, oauth_accounts=oauth_accounts)
        return user

    async def delete(self, user: UD) -> None:
        await self.model.objects.delete(id=user.id)
