import databases
import sqlalchemy
from fastapi import FastAPI
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTable,
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase,
)
from httpx_oauth.clients.google import GoogleOAuth2
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from starlette.requests import Request

DATABASE_URL = "sqlite:///./test.db"
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


database = databases.Database(DATABASE_URL)
Base: DeclarativeMeta = declarative_base()


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable, Base):
    pass


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)

users = UserTable.__table__
oauth_accounts = OAuthAccount.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users, oauth_accounts)


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


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
