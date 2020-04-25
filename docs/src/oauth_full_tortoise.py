from fastapi import FastAPI
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import (
    TortoiseBaseOAuthAccountModel,
    TortoiseBaseUserModel,
    TortoiseUserDatabase,
)
from httpx_oauth.clients.google import GoogleOAuth2
from starlette.requests import Request
from tortoise import fields
from tortoise.contrib.starlette import register_tortoise

DATABASE_URL = "sqlite://./test.db"
SECRET = "SECRET"


google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")


class User(models.BaseUser, models.BaseOAuthAccountMixin):
    pass


class UserCreate(User, models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


class UserModel(TortoiseBaseUserModel):
    pass


class OAuthAccountModel(TortoiseBaseOAuthAccountModel):
    user = fields.ForeignKeyField("models.UserModel", related_name="oauth_accounts")


user_db = TortoiseUserDatabase(UserDB, UserModel, OAuthAccountModel)
app = FastAPI()
register_tortoise(app, db_url=DATABASE_URL, modules={"models": ["test"]})

auth_backends = [
    JWTAuthentication(secret=SECRET, lifetime_seconds=3600),
]

fastapi_users = FastAPIUsers(
    user_db, auth_backends, User, UserCreate, UserUpdate, UserDB, SECRET,
)
app.include_router(fastapi_users.router, prefix="/users", tags=["users"])

google_oauth_router = fastapi_users.get_oauth_router(google_oauth_client, SECRET)
app.include_router(google_oauth_router, prefix="/google-oauth", tags=["users"])


@fastapi_users.on_after_register()
def on_after_register(user: User, request: Request):
    print(f"User {user.id} has registered.")


@fastapi_users.on_after_forgot_password()
def on_after_forgot_password(user: User, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")
