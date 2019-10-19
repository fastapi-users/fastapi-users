import databases
import sqlalchemy
from fastapi import FastAPI
from fastapi_users import BaseUser, FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

DATABASE_URL = "sqlite:///./test.db"
SECRET = "SECRET"


database = databases.Database(DATABASE_URL)

Base: DeclarativeMeta = declarative_base()


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

Base.metadata.create_all(engine)

users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(database, users)


class User(BaseUser):
    pass


auth = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)


def on_after_forgot_password(user, token):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


app = FastAPI()
fastapi_users = FastAPIUsers(user_db, auth, User, on_after_forgot_password, SECRET)
app.include_router(fastapi_users.router, prefix="/users", tags=["users"])


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
