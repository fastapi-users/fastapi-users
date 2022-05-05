# Database

The most natural way for storing tokens is of course the very same database you're using for your application. In this strategy, we set up a table (or collection) for storing those tokens with the associated user id. On each request, we try to retrive this token from the database to get the corresponding user id.

## Configuration

The configuration of this strategy is a bit more complex than the others as it requires you to configure models and a database adapter, [exactly like we did for users](../../overview.md#user-model-and-database-adapters).


### Database adapters

An access token will be structured like this in your database:

* `token` (`str`) – Unique identifier of the token. It's generated automatically upon login by the strategy.
* `user_id` (`ID`) – User id. of the user associated to this token.
* `created_at` (`datetime`) – Date and time of creation of the token. It's used to determine if the token is expired or not.

We are providing a base model with those fields for each database we are supporting.

#### SQLAlchemy

We'll expand from the basic SQLAlchemy configuration.

```py hl_lines="5-8 21-22 43-46"
--8<-- "docs/src/db_sqlalchemy_access_tokens.py"
```

1. We define an `AccessToken` ORM model inheriting from `SQLAlchemyBaseAccessTokenTableUUID`.

2. We define a dependency to instantiate the `SQLAlchemyAccessTokenDatabase` class. Just like the user database adapter, it expects a fresh SQLAlchemy session and the `AccessToken` model class we defined above.

!!! tip "`user_id` foreign key is defined as UUID"
    By default, we use UUID as a primary key ID for your user, so we follow the same convention to define the foreign key pointing to the user.

    If you want to use another type, like an auto-incremented integer, you can use `SQLAlchemyBaseAccessTokenTable` as base class and define your own `user_id` column.

    ```py
    class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):
        @declared_attr
        def user_id(cls):
            return Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
    ```

    Notice that `SQLAlchemyBaseAccessTokenTable` expects a generic type to define the actual type of ID you use.

#### Beanie

We'll expand from the basic Beanie configuration.

```py hl_lines="4-7 20-21 28-29"
--8<-- "docs/src/db_beanie_access_tokens.py"
```

1. We define an `AccessToken` ODM model inheriting from `BeanieBaseAccessToken`. Notice that we set a generic type to define the type of the `user_id` reference. By default, it's a standard MongoDB ObjectID.

2. We define a dependency to instantiate the `BeanieAccessTokenDatabase` class. Just like the user database adapter, it expects the `AccessToken` model class we defined above.


### Strategy

```py
import uuid

from fastapi import Depends
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from .db import AccessToken, User


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)
```

As you can see, instantiation is quite simple. It accepts the following arguments:

* `database` (`AccessTokenDatabase`): A database adapter instance for `AccessToken` table, like we defined above.
* `lifetime_seconds` (`int`): The lifetime of the token in seconds.

!!! tip "Why it's inside a function?"
    To allow strategies to be instantiated dynamically with other dependencies, they have to be provided as a callable to the authentication backend.

    As you can see here, this pattern allows us to dynamically inject a connection to the database.

## Logout

On logout, this strategy will delete the token from the database.
