# 9.x.x ➡️ 10.x.x

Version 10 marks important changes in how we manage User models and their ID.

Before, we were relying only on Pydantic models to work with users. In particular the [`current_user` dependency](../usage/current-user.md) would return you an instance of `UserDB`, a Pydantic model. This proved to be quite problematic with some ORM if you ever needed to **retrieve relationship data** or make specific requests.

Now, FastAPI Users is designed to always return you a **native object for your ORM model**, whether it's an SQLAlchemy model or a Beanie document. Pydantic models are now only used for validation and serialization inside the API.

Before, we were forcing the use of UUID as primary key ID; a consequence of the design above. This proved to be quite problematic on some databases, like MongoDB which uses a special ObjectID format by default. Some SQL folks also prefer to use traditional auto-increment integers.

Now, FastAPI Users is designed to use **generic ID type**. It means that you can use any type you want for your user's ID. By default, SQLAlchemy adapter still use UUID; but you can quite easily switch to another thing, like an integer. Beanie adapter for MongoDB will use native ObjectID by default, but it also can be overriden.

As you may have guessed, those changes imply quite a lot of **breaking changes**.

## User models and database adapter

### SQLAlchemy ORM

We've removed the old SQLAlchemy dependency support, so the dependency is now `fastapi-users[sqlalchemy]`.

=== "Before"

    ```txt
    fastapi
    fastapi-users[sqlalchemy2]
    uvicorn[standard]
    aiosqlite
    ```

=== "After"


    ```txt
    fastapi
    fastapi-users[sqlalchemy]
    uvicorn[standard]
    aiosqlite
    ```

The User model base class for SQLAlchemy slightly changed to support UUID by default.

We changed the name of the class from `UserTable` to `User`: it's not a compulsory change, but since there is no risk of confusion with Pydantic models anymore, it's probably a more idiomatic naming.

=== "Before"

    ```py
    class UserTable(Base, SQLAlchemyBaseUserTable):
        pass
    ```

=== "After"

    ```py
    class User(SQLAlchemyBaseUserTableUUID, Base):
        pass
    ```

Instantiating the `SQLAlchemyUserDatabase` adapter now only expects this `User` model. `UserDB` is removed.

=== "Before"

    ```py
    async def get_user_db(session: AsyncSession = Depends(get_async_session)):
        yield SQLAlchemyUserDatabase(UserDB, session, UserTable)
    ```

=== "After"

    ```py
    async def get_user_db(session: AsyncSession = Depends(get_async_session)):
        yield SQLAlchemyUserDatabase(session, User)
    ```

### MongoDB

MongoDB support is now only provided through [Beanie ODM](https://github.com/roman-right/beanie/). Even if you don't use it for the rest of your project, it's a very light addition that shouldn't interfere much.

=== "Before"

    ```txt
    fastapi
    fastapi-users[mongodb]
    uvicorn[standard]
    aiosqlite
    ```

=== "After"


    ```txt
    fastapi
    fastapi-users[beanie]
    uvicorn[standard]
    aiosqlite
    ```

You now need to define a proper User model using Beanie.

=== "Before"

    ```py
    import os

    import motor.motor_asyncio
    from fastapi_users.db import MongoDBUserDatabase

    from app.models import UserDB

    DATABASE_URL = os.environ["DATABASE_URL"]
    client = motor.motor_asyncio.AsyncIOMotorClient(
        DATABASE_URL, uuidRepresentation="standard"
    )
    db = client["database_name"]
    collection = db["users"]


    async def get_user_db():
        yield MongoDBUserDatabase(UserDB, collection)
    ```

=== "After"

    ```py
    import motor.motor_asyncio
    from beanie import PydanticObjectId
    from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase

    DATABASE_URL = "mongodb://localhost:27017"
    client = motor.motor_asyncio.AsyncIOMotorClient(
        DATABASE_URL, uuidRepresentation="standard"
    )
    db = client["database_name"]


    class User(BeanieBaseUser[PydanticObjectId]):
        pass


    async def get_user_db():
        yield BeanieUserDatabase(User)
    ```

!!! danger "ID are now ObjectID by default"
    By default, User ID will now be native MongoDB ObjectID. If you don't want to make the transition and keep UUID you can do so by overriding the `id` field:

    ```py
    import uuid

    from pydantic import Field


    class User(BeanieBaseUser[uuid.UUID]):
        id: uuid.UUID = Field(default_factory=uuid.uuid4)
    ```

Beanie also needs to be initialized in a startup event handler of your FastAPI app:

```py
from beanie import init_beanie


@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=db,
        document_models=[
            User,
        ],
    )
```

### Tortoise ORM and ormar

Unfortunately, we sometimes need to make difficult choices to keep things sustainable. That's why we decided to **not support Tortoise ORM and ormar** anymore. It appeared they were not widely used.

You can still add support for those ORM yourself by implementing the necessary adapter. You can take inspiration from [the SQLAlchemy one](https://github.com/fastapi-users/fastapi-users-db-sqlalchemy).

## `UserManager`

There is some slight changes on the `UserManager` class. In particular, it now needs a `parse_id` method that can be provided through built-in mixins.

Generic typing now expects your **native User model class** and the **type of ID**.

The `user_db_model` class property is **removed**.

=== "Before"

    ```py
    class UserManager(BaseUserManager[UserCreate, UserDB]):
        user_db_model = UserDB
        reset_password_token_secret = SECRET
        verification_token_secret = SECRET

        async def on_after_register(self, user: UserDB, request: Optional[Request] = None):
            print(f"User {user.id} has registered.")

        async def on_after_forgot_password(
            self, user: UserDB, token: str, request: Optional[Request] = None
        ):
            print(f"User {user.id} has forgot their password. Reset token: {token}")

        async def on_after_request_verify(
            self, user: UserDB, token: str, request: Optional[Request] = None
        ):
            print(f"Verification requested for user {user.id}. Verification token: {token}")
    ```

=== "After"

    ```py
    class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
        reset_password_token_secret = SECRET
        verification_token_secret = SECRET

        async def on_after_register(self, user: User, request: Optional[Request] = None):
            print(f"User {user.id} has registered.")

        async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
        ):
            print(f"User {user.id} has forgot their password. Reset token: {token}")

        async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
        ):
            print(f"Verification requested for user {user.id}. Verification token: {token}")
    ```

If you need to support other types of ID, you can read more about it [in the dedicated section](../configuration/user-manager.md#the-id-parser-mixin).

## Pydantic models

To better distinguish them from the ORM models, Pydantic models are now called **schemas**.

**`UserDB` has been removed** in favor of native models.

We changed the name of `User` to `UserRead`: it's not a compulsory change, but since there is a **risk of confusion** with the native model, it's highly recommended.

Besides, the `BaseUser` schema now accepts a generic type to specify the type of ID you use.

=== "Before"

    ```py
    from fastapi_users import models


    class User(models.BaseUser):
        pass


    class UserCreate(models.BaseUserCreate):
        pass


    class UserUpdate(models.BaseUserUpdate):
        pass


    class UserDB(User, models.BaseUserDB):
        pass
    ```

=== "After"

    ```py
    import uuid

    from fastapi_users import schemas


    class UserRead(schemas.BaseUser[uuid.UUID]):
        pass


    class UserCreate(schemas.BaseUserCreate):
        pass


    class UserUpdate(schemas.BaseUserUpdate):
        pass
    ```

## FastAPI Users and routers

Pydantic schemas are now way less important in this new design. As such, you don't need to pass them when initializing the `FastAPIUsers` class:

=== "Before"

    ```py
    fastapi_users = FastAPIUsers(
        get_user_manager,
        [auth_backend],
        User,
        UserCreate,
        UserUpdate,
        UserDB,
    )
    ```

=== "After"

    ```py
    fastapi_users = FastAPIUsers[User, uuid.UUID](
        get_user_manager,
        [auth_backend],
    )
    ```

As a consequence, those schemas need to be passed when initializing the router that needs them: `get_register_router`, `get_verify_router` and `get_users_router`.

=== "Before"

    ```py
    app.include_router(
        fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
    )
    app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["auth"])
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])
    ```

=== "After"

    ```py
    app.include_router(
        fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )
    ```

## Lost?

If you're unsure or a bit lost, make sure to check the [full working examples](../configuration/full-example.md).
