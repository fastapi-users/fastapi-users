from typing import Any, List, Optional, Type, cast

import ormar
from ormar.exceptions import NoMatch
from pydantic import UUID4

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD, BaseOAuthAccount


class OrmarBaseUserModel(ormar.Model):
    class Meta:
        tablename = "users"
        abstract = True

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

    async def get(self, id: UUID4) -> Optional[UD]:
        return await self._get_user(id=id)

    async def get_by_email(self, email: str) -> Optional[UD]:
        return await self._get_user(email__iexact=email)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UD]:
        return await self._get_user(
            oauth_accounts__oauth_name=oauth, oauth_accounts__account_id=account_id
        )

    async def create(self, user: UD) -> UD:
        oauth_accounts = getattr(user, "oauth_accounts", [])
        model = await self.model(**user.dict(exclude={"oauth_accounts"})).save()
        if oauth_accounts and self.oauth_account_model:
            await self._create_oauth_models(model=model, oauth_accounts=oauth_accounts)
        user_db = await self._get_user(id=user.id)
        return cast(UD, user_db)

    async def update(self, user: UD) -> UD:
        oauth_accounts = getattr(user, "oauth_accounts", [])
        model = await self._get_db_user(id=user.id)
        await model.update(**user.dict(exclude={"oauth_accounts"}))
        if oauth_accounts and self.oauth_account_model:
            await model.oauth_accounts.clear(keep_reversed=False)
            await self._create_oauth_models(model=model, oauth_accounts=oauth_accounts)
        user_db = await self._get_user(id=user.id)
        return cast(UD, user_db)

    async def delete(self, user: UD) -> None:
        await self.model.objects.delete(id=user.id)

    async def _create_oauth_models(
        self, model: OrmarBaseUserModel, oauth_accounts: List[BaseOAuthAccount]
    ):
        if self.oauth_account_model:
            oauth_accounts_db = [
                self.oauth_account_model(user=model, **oacc.dict())
                for oacc in oauth_accounts
            ]
            await self.oauth_account_model.objects.bulk_create(oauth_accounts_db)

    async def _get_db_user(self, **kwargs: Any) -> OrmarBaseUserModel:
        query = self.model.objects.filter(**kwargs)
        if self.oauth_account_model is not None:
            query = query.select_related("oauth_accounts")
        return cast(OrmarBaseUserModel, await query.get())

    async def _get_user(self, **kwargs: Any) -> Optional[UD]:
        try:
            user = await self._get_db_user(**kwargs)
        except NoMatch:
            return None
        return self.user_db_model(**user.dict())
