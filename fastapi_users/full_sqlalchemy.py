import databases
import sqlalchemy
from fastapi import Depends, FastAPI
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import CookieAuthentication, JWTAuthentication
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

DATABASE_URL = "sqlite:///./test.db"
SECRET = "SECRET"


class User(models.BaseUser):
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


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)

users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)


auth_backends = [
    JWTAuthentication(secret=SECRET, lifetime_seconds=3600),
    CookieAuthentication(secret=SECRET, lifetime_seconds=3600),
]

app = FastAPI()
fastapi_users = FastAPIUsers(
    user_db, auth_backends, User, UserCreate, UserUpdate, UserDB
)
app.include_router(fastapi_users.get_register_router(), tags=["auth"])
app.include_router(
    fastapi_users.get_reset_password_router("SECRET"), tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(), prefix="/users", tags=["users"]
)
app.include_router(
    fastapi_users.get_auth_router(auth_backends[0]), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_auth_router(auth_backends[1]),
    prefix="/auth/cookie",
    tags=["auth"],
)


@app.get("/test")
def test(u=Depends(fastapi_users.get_current_active_user)):
    return u


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
