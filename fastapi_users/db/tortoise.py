from typing import Optional, Type

from pydantic import UUID4
from tortoise import fields, models
from tortoise.exceptions import DoesNotExist

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD


class TortoiseBaseUserModel(models.Model):
    id = fields.UUIDField(pk=True, generated=False)
    email = fields.CharField(index=True, unique=True, null=False, max_length=255)
    hashed_password = fields.CharField(null=False, max_length=255)
    is_active = fields.BooleanField(default=True, null=False)
    is_superuser = fields.BooleanField(default=False, null=False)
    is_verified = fields.BooleanField(default=False, null=False)

    async def to_dict(self):
        d = {}
        for field in self._meta.db_fields:
            d[field] = getattr(self, field)
        for field in self._meta.backward_fk_fields:
            d[field] = await getattr(self, field).all().values()
        return d

    class Meta:
        abstract = True


class TortoiseBaseOAuthAccountModel(models.Model):
    id = fields.UUIDField(pk=True, generated=False, max_length=255)
    oauth_name = fields.CharField(null=False, max_length=255)
    access_token = fields.CharField(null=False, max_length=255)
    expires_at = fields.IntField(null=True)
    refresh_token = fields.CharField(null=True, max_length=255)
    account_id = fields.CharField(index=True, null=False, max_length=255)
    account_email = fields.CharField(null=False, max_length=255)

    class Meta:
        abstract = True


class TortoiseUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for Tortoise ORM.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param model: Tortoise ORM model.
    :param oauth_account_model: Optional Tortoise ORM model of a OAuth account.
    """

    model: Type[TortoiseBaseUserModel]
    oauth_account_model: Optional[Type[TortoiseBaseOAuthAccountModel]]

    def __init__(
        self,
        user_db_model: Type[UD],
        model: Type[TortoiseBaseUserModel],
        oauth_account_model: Optional[Type[TortoiseBaseOAuthAccountModel]] = None,
    ):
        super().__init__(user_db_model)
        self.model = model
        self.oauth_account_model = oauth_account_model

    async def get(self, id: UUID4) -> Optional[UD]:
        try:
            query = self.model.get(id=id)

            if self.oauth_account_model is not None:
                query = query.prefetch_related("oauth_accounts")

            user = await query
            user_dict = await user.to_dict()

            return self.user_db_model(**user_dict)
        except DoesNotExist:
            return None

    async def get_by_email(self, email: str) -> Optional[UD]:
        query = self.model.filter(email__iexact=email).first()

        if self.oauth_account_model is not None:
            query = query.prefetch_related("oauth_accounts")

        user = await query

        if user is None:
            return None

        user_dict = await user.to_dict()
        return self.user_db_model(**user_dict)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UD]:
        try:
            query = self.model.get(
                oauth_accounts__oauth_name=oauth, oauth_accounts__account_id=account_id
            ).prefetch_related("oauth_accounts")

            user = await query
            user_dict = await user.to_dict()

            return self.user_db_model(**user_dict)
        except DoesNotExist:
            return None

    async def create(self, user: UD) -> UD:
        user_dict = user.dict()
        oauth_accounts = user_dict.pop("oauth_accounts", None)

        model = self.model(**user_dict)
        await model.save()

        if oauth_accounts and self.oauth_account_model:
            oauth_account_objects = []
            for oauth_account in oauth_accounts:
                oauth_account_objects.append(
                    self.oauth_account_model(user=model, **oauth_account)
                )
            await self.oauth_account_model.bulk_create(oauth_account_objects)

        return user

    async def update(self, user: UD) -> UD:
        user_dict = user.dict()
        user_dict.pop("id")  # Tortoise complains if we pass the PK again
        oauth_accounts = user_dict.pop("oauth_accounts", None)

        model = await self.model.get(id=user.id)
        for field in user_dict:
            setattr(model, field, user_dict[field])
        await model.save()

        if oauth_accounts and self.oauth_account_model:
            await model.oauth_accounts.all().delete()
            oauth_account_objects = []
            for oauth_account in oauth_accounts:
                oauth_account_objects.append(
                    self.oauth_account_model(user=model, **oauth_account)
                )
            await self.oauth_account_model.bulk_create(oauth_account_objects)

        return user

    async def delete(self, user: UD) -> None:
        await self.model.filter(id=user.id).delete()
