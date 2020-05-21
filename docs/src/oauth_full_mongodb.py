import motor.motor_asyncio
from fastapi import FastAPI
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import MongoDBUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from starlette.requests import Request

DATABASE_URL = "mongodb://localhost:27017"
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


client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["database_name"]
collection = db["users"]
user_db = MongoDBUserDatabase(UserDB, collection)

auth_backends = [
    JWTAuthentication(secret=SECRET, lifetime_seconds=3600),
]

app = FastAPI()
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
