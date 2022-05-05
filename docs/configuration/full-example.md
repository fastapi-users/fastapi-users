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

## What now?

You're ready to go! Be sure to check the [Usage](../usage/routes.md) section to understand how to work with **FastAPI Users**.
