# Full example

Here is a full working example with JWT authentication to help get you started.

!!! warning
    Notice that **SECRET** should be changed to a strong passphrase.
    Insecure passwords may give attackers full access to your database.

## SQLAlchemy

[Open :octicons-link-external-16:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/sqlalchemy)

=== ":octicons-file-code-16: requirements.txt"

    ```
    --8<-- "examples/sqlalchemy/requirements.txt"
    ```

=== ":octicons-file-code-16: main.py"

    ```py
    --8<-- "examples/sqlalchemy/main.py"
    ```

=== ":octicons-file-code-16: app/app.py"

    ```py
    --8<-- "examples/sqlalchemy/app/app.py"
    ```

=== ":octicons-file-code-16: app/db.py"

    ```py
    --8<-- "examples/sqlalchemy/app/db.py"
    ```

=== ":octicons-file-code-16: app/models.py"

    ```py
    --8<-- "examples/sqlalchemy/app/models.py"
    ```

=== ":octicons-file-code-16: app/users.py"

    ```py
    --8<-- "examples/sqlalchemy/app/users.py"
    ```

## MongoDB

[Open :octicons-link-external-16:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/mongodb)

=== ":octicons-file-code-16: requirements.txt"

    ```
    --8<-- "examples/mongodb/requirements.txt"
    ```

=== ":octicons-file-code-16: main.py"

    ```py
    --8<-- "examples/mongodb/main.py"
    ```

=== ":octicons-file-code-16: app/app.py"

    ```py
    --8<-- "examples/mongodb/app/app.py"
    ```

=== ":octicons-file-code-16: app/db.py"

    ```py
    --8<-- "examples/mongodb/app/db.py"
    ```

=== ":octicons-file-code-16: app/models.py"

    ```py
    --8<-- "examples/mongodb/app/models.py"
    ```

=== ":octicons-file-code-16: app/users.py"

    ```py
    --8<-- "examples/mongodb/app/users.py"
    ```

## Tortoise ORM

[Open :octicons-link-external-16:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/tortoise)

=== ":octicons-file-code-16: requirements.txt"

    ```
    --8<-- "examples/tortoise/requirements.txt"
    ```

=== ":octicons-file-code-16: main.py"

    ```py
    --8<-- "examples/tortoise/main.py"
    ```

=== ":octicons-file-code-16: app/app.py"

    ```py
    --8<-- "examples/tortoise/app/app.py"
    ```

=== ":octicons-file-code-16: app/db.py"

    ```py
    --8<-- "examples/tortoise/app/db.py"
    ```

=== ":octicons-file-code-16: app/models.py"

    ```py
    --8<-- "examples/tortoise/app/models.py"
    ```

=== ":octicons-file-code-16: app/users.py"

    ```py
    --8<-- "examples/tortoise/app/users.py"
    ```

## What now?

You're ready to go! Be sure to check the [Usage](../usage/routes.md) section to understand how to work with **FastAPI Users**.
