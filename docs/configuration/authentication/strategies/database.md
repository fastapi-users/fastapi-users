# Database

The most natural way for storing tokens is of course the very same database you're using for your application. In this strategy, we set up a table (or collection) for storing those tokens with the associated user id. On each request, we try to retrive this token from the database to get the corresponding user id.

## Configuration

The configuration of this strategy is a bit more complex than the others as it requires you to configure models and a database adapter, [exactly like we did for users](../../overview.md#database-adapters).


### Model

You should define an `AccessToken` Pydantic model inheriting from `BaseAccessToken`.

```py
from fastapi_users.authentication.strategy.db import BaseAccessToken


class AccessToken(BaseAccessToken):
        pass
```

It is structured like this:

* `token` (`str`) – Unique identifier of the token. It's generated automatically upon login by the strategy.
* `user_id` (`UUID4`) – User id. of the user associated to this token.
* `created_at` (`datetime`) – Date and time of creation of the token. It's used to determine if the token is expired or not.

### Database adapter

=== "SQLAlchemy"

    ```py hl_lines="5-8 13 23-24 45-46"
    --8<-- "docs/src/db_sqlalchemy_access_tokens.py"
    ```

=== "Tortoise ORM"

    With Tortoise ORM, you need to define a proper Tortoise model for `AccessToken` and manually specify the user foreign key. Besides, you need to modify the Pydantic model a bit so that it works well with this Tortoise model.

    === ":octicons-file-code-16: model.py"
        ```py hl_lines="2 4 31-38"
        --8<-- "docs/src/db_tortoise_access_tokens_model.py"
        ```

    === ":octicons-file-code-16: adapter.py"
        ```py hl_lines="2 4 13-14"
        --8<-- "docs/src/db_tortoise_access_tokens_adapter.py"
        ```

=== "MongoDB"

    ```py hl_lines="3 5 13 20-21"
    --8<-- "docs/src/db_mongodb_access_tokens.py"
    ```


### Strategy

```py
from fastapi import Depends
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from .models import AccessToken, UserCreate, UserDB


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy[UserCreate, UserDB, AccessToken]:
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
