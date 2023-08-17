# Full example

Here is a full working example with JWT authentication to help get you started.

!!! warning
    Notice that **SECRET** should be changed to a strong passphrase.
    Insecure passwords may give attackers full access to your database.

## SQLAlchemy

[Open :material-open-in-new:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/sqlalchemy)

=== "requirements.txt"

    ```
    --8<-- "examples/sqlalchemy/requirements.txt"
    ```

=== "main.py"

    ```py
    --8<-- "examples/sqlalchemy/main.py"
    ```

=== "app/app.py"

    ```py
    --8<-- "examples/sqlalchemy/app/app.py"
    ```

=== "app/db.py"

    ```py
    --8<-- "examples/sqlalchemy/app/db.py"
    ```

=== "app/schemas.py"

    ```py
    --8<-- "examples/sqlalchemy/app/schemas.py"
    ```

=== "app/users.py"

    ```py
    --8<-- "examples/sqlalchemy/app/users.py"
    ```

## Beanie

[Open :material-open-in-new:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/beanie)

=== "requirements.txt"

    ```
    --8<-- "examples/beanie/requirements.txt"
    ```

=== "main.py"

    ```py
    --8<-- "examples/beanie/main.py"
    ```

=== "app/app.py"

    ```py
    --8<-- "examples/beanie/app/app.py"
    ```

=== "app/db.py"

    ```py
    --8<-- "examples/beanie/app/db.py"
    ```

=== "app/schemas.py"

    ```py
    --8<-- "examples/beanie/app/schemas.py"
    ```

=== "app/users.py"

    ```py
    --8<-- "examples/beanie/app/users.py"
    ```

## SQLModel

[Open :material-open-in-new:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/sqlmodel)

=== "requirements.txt"

    ```
    --8<-- "examples/sqlmodel/requirements.txt"
    ```

=== "main.py"

    ```py
    --8<-- "examples/sqlmodel/main.py"
    ```

=== "app/app.py"

    ```py
    --8<-- "examples/sqlmodel/app/app.py"
    ```

=== "app/db.py"

    ```py
    --8<-- "examples/sqlmodel/app/db.py"
    ```

=== "app/schemas.py"

    ```py
    --8<-- "examples/sqlmodel/app/schemas.py"
    ```

=== "app/users.py"

    ```py
    --8<-- "examples/sqlmodel/app/users.py"
    ```

!!! note

    You will notice that the [SQLModel](https://sqlmodel.tiangolo.com/) example is very similar
    to the [SQLAlchemy](#sqlalchemy) example. This is because SQLModel is built on top of SQLAlchemy
    and pydantic.

    There are a few important differences you should take note of:

    #### `app/db.py`

    - Removing the `DeclarativeBase` SQLAlchemy base class.
    - Using `fastapi_users.db.SQLModelBaseUserDB` instead of
      `fastapi_users.db.SQLAlchemyBaseUserTable`.
    - Using `fastapi_users.db.SQLModelUserDatabaseAsync` instead of
      `fastapi_users.db.SQLAlchemyUserDatabase`.
    - Setting the `class_` parameter of `sessionmaker` to `AsyncSession`.
    - Using `SQLModel.metadata.create_all` instead of `Base.metadata.create_all`.

    #### `app/users.py`

    - Using `fastapi_users.db.SQLModelUserDatabaseAsync` instead of
      `fastapi_users.db.SQLAlchemyUserDatabase`.


## What now?

You're ready to go! Be sure to check the [Usage](../usage/routes.md) section to understand how to work with **FastAPI Users**.
