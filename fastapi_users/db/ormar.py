from typing import Optional, Type
from pydantic import UUID4
import ormar
from ormar.exceptions import NoMatch
from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD


class OrmarBaseUserModel(ormar.Model):
    class Meta:
        abstract = True

    # tortoise:
    # id = fields.UUIDField(pk=True, generated=False)
    id = ormar.UUID(primary_key=True)
    # XXX: uuid_format?
    # UUID(uuid_format: str = 'hex')

    # tortoise:
    # email = fields.CharField(index=True, unique=True, null=False, max_length=255)
    email = ormar.String(index=True, unique=True,
                         nullable=False, max_length=255)

    # tortoise:
    # hashed_password = fields.CharField(null=False, max_length=255)
    hashed_password = ormar.String(nullable=False, max_length=255)

    # tortoise:
    # is_active = fields.BooleanField(default=True, null=False)
    is_active = ormar.Boolean(default=True, nullable=False)

    # tortoise:
    # is_superuser = fields.BooleanField(default=False, null=False)
    is_superuser = ormar.Boolean(default=False, nullable=False)

    # tortoise:
    # is_verified = fields.BooleanField(default=False, null=False)
    is_verified = ormar.Boolean(default=False, nullable=False)


class OrmarBaseOAuthAccountModel(ormar.Model):
    # TODO
    class Meta:
        abstract = True

    # id = ormar.UUID(primary_key=True)
    # oauth_name
    # access_token
    # expires_at
    # refresh_token
    # account_id
    # account_email


class OrmarUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for ormar.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param model: ormar ORM model.
    :param oauth_account_model: Optional ormar model of a OAuth account.
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
        try:
            # tortise:
            # query = self.model.get(id=id)
            query = self.model.objects.filter(id=id)

            if self.oauth_account_model is not None:
                # tortise:
                # query = query.prefetch_related("oauth_accounts")
                query = query.prefetch_related("oauth_accounts")

            try:
                user = await query.first()
            except NoMatch:
                return None

            user_dict = user.dict()
            return self.user_db_model(**user_dict)
        except NoMatch:
            return None

    async def get_by_email(self, email: str) -> Optional[UD]:
        query = self.model.objects.filter(email__iexact=email)

        if self.oauth_account_model is not None:
            query = query.prefetch_related("oauth_accounts")

        try:
            user = await query.first()
        except NoMatch:
            return None

        user_dict = user.dict()
        return self.user_db_model(**user_dict)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UD]:
        # TODO
        try:
            query = self.model.get(
                oauth_accounts__oauth_name=oauth, oauth_accounts__account_id=account_id
            ).prefetch_related("oauth_accounts")

            user = await query
            user_dict = await user.to_dict()

            return self.user_db_model(**user_dict)
        except NoMatch:
            return None

    async def create(self, user: UD) -> UD:
        user_dict = user.dict()
        oauth_accounts = user_dict.pop("oauth_accounts", None)

        model = self.model(**user_dict)
        await model.save()

        # TODO
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
        # user_dict.pop("id")  # Tortoise complains if we pass the PK again
        oauth_accounts = user_dict.pop("oauth_accounts", None)

        model = await self.model.objects.get(id=user.id)
        for field in user_dict:
            setattr(model, field, user_dict[field])
        # XXX: the following update gives
        # sqlite3.IntegrityError: UNIQUE constraint failed: users.email
        # when a user mail is updated with the same mail of another existing user
        # how to handle this case?
        await model.update()

        # TODO
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
        await self.model.objects.filter(id=user.id).delete()
