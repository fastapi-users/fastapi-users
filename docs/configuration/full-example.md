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

=== "app/models.py"

    ```py
    --8<-- "examples/sqlalchemy/app/models.py"
    ```

=== "app/users.py"

    ```py
    --8<-- "examples/sqlalchemy/app/users.py"
    ```

## MongoDB

[Open :material-open-in-new:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/mongodb)

=== "requirements.txt"

    ```
    --8<-- "examples/mongodb/requirements.txt"
    ```

=== "main.py"

    ```py
    --8<-- "examples/mongodb/main.py"
    ```

=== "app/app.py"

    ```py
    --8<-- "examples/mongodb/app/app.py"
    ```

=== "app/db.py"

    ```py
    --8<-- "examples/mongodb/app/db.py"
    ```

=== "app/models.py"

    ```py
    --8<-- "examples/mongodb/app/models.py"
    ```

=== "app/users.py"

    ```py
    --8<-- "examples/mongodb/app/users.py"
    ```

## Tortoise ORM

[Open :material-open-in-new:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/tortoise)

=== "requirements.txt"

    ```
    --8<-- "examples/tortoise/requirements.txt"
    ```

=== "main.py"

    ```py
    --8<-- "examples/tortoise/main.py"
    ```

=== "app/app.py"

    ```py
    --8<-- "examples/tortoise/app/app.py"
    ```

=== "app/db.py"

    ```py
    --8<-- "examples/tortoise/app/db.py"
    ```

=== "app/models.py"

    ```py
    --8<-- "examples/tortoise/app/models.py"
    ```

=== "app/users.py"

    ```py
    --8<-- "examples/tortoise/app/users.py"
    ```

## What now?

You're ready to go! Be sure to check the [Usage](../usage/routes.md) section to understand how to work with **FastAPI Users**.
