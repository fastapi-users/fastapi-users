from fastapi import FastAPI, Request
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import (
    TortoiseBaseOAuthAccountModel,
    TortoiseBaseUserModel,
    TortoiseUserDatabase,
)
from httpx_oauth.clients.google import GoogleOAuth2
from tortoise import fields
from tortoise.contrib.starlette import register_tortoise

DATABASE_URL = "sqlite://./test.db"
SECRET = "SECRET"


google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")


class User(models.BaseUser, models.BaseOAuthAccountMixin):
    pass


class UserCreate(models.BaseUserCreate):
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


def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")


def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=3600, tokenUrl="/auth/jwt/login"
)

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(on_after_register), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(
        SECRET, after_forgot_password=on_after_forgot_password
    ),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])

google_oauth_router = fastapi_users.get_oauth_router(
    google_oauth_client, SECRET, after_register=on_after_register
)
app.include_router(google_oauth_router, prefix="/auth/google", tags=["auth"])
