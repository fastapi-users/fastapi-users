# OAuth2

FastAPI Users provides an optional OAuth2 authentication support. It relies on [HTTPX OAuth library](https://frankie567.github.io/httpx-oauth/), which is a pure-async implementation of OAuth2.

## Installation

You should install the library with the optional dependencies for OAuth:

```sh
pip install 'fastapi-users[sqlalchemy2,oauth]'
```

```sh
pip install 'fastapi-users[mongodb,oauth]'
```

```sh
pip install 'fastapi-users[tortoise-orm,oauth]'
```

## Configuration

### Instantiate an OAuth2 client

You first need to get an HTTPX OAuth client instance. [Read the documentation](https://frankie567.github.io/httpx-oauth/oauth2/) for more information.

```py
from httpx_oauth.clients.google import GoogleOAuth2

google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")
```

### Setup the models

The user models differ a bit from the standard one as we have to have a way to store the OAuth information (access tokens, account ids...).

```py
from fastapi_users import models


class User(models.BaseUser, models.BaseOAuthAccountMixin):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass
```

Notice that we inherit from the `BaseOAuthAccountMixin`, which adds a `List` of `BaseOAuthAccount` objects. This object is structured like this:

* `id` (`UUID4`) – Unique identifier of the OAuth account information. Defaults to a **UUID4**.
* `oauth_name` (`str`) – Name of the OAuth service. It corresponds to the `name` property of the OAuth client.
* `access_token` (`str`) – Access token.
* `expires_at` (`Optional[int]`) - Timestamp at which the access token is expired.
* `refresh_token` (`Optional[str]`) – On services that support it, a token to get a fresh access token.
* `account_id` (`str`) - Identifier of the OAuth account on the corresponding service.
* `account_email` (`str`) - Email address of the OAuth account on the corresponding service.

### Setup the database adapter

#### SQLAlchemy

You'll need to define the SQLAlchemy model for storing OAuth accounts. We provide a base one for this:

```py hl_lines="19-24"
--8<-- "docs/src/db_sqlalchemy_oauth.py"
```

Notice that we also manually added a `relationship` on the `UserTable` so that SQLAlchemy can properly retrieve the OAuth accounts of the user.

When instantiating the database adapter, you should pass this SQLAlchemy model:

```py hl_lines="41-42"
--8<-- "docs/src/db_sqlalchemy_oauth.py"
```

#### MongoDB

Nothing to do, the [basic configuration](./databases/mongodb.md) is enough.

#### Tortoise ORM

You'll need to define the Tortoise model for storing the OAuth account model. We provide a base one for this:

```py hl_lines="29 30"
--8<-- "docs/src/db_tortoise_oauth_model.py"
```

!!! warning
    Note that you should define the foreign key yourself, so that you can point it the user model in your namespace.

Then, you should declare it on the database adapter:

```py hl_lines="8 9"
--8<-- "docs/src/db_tortoise_oauth_adapter.py"
```

### Generate a router

Once you have a `FastAPIUsers` instance, you can make it generate a single OAuth router for a given client **and** authentication backend.

```py
app.include_router(
  fastapi_users.get_oauth_router(google_oauth_client, auth_backend, "SECRET"),
  prefix="/auth/google",
  tags=["auth"],
)
```

### Full example

!!! warning
    Notice that **SECRET** should be changed to a strong passphrase.
    Insecure passwords may give attackers full access to your database.

#### SQLAlchemy

[Open :octicons-link-external-16:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/sqlalchemy-oauth)

=== ":octicons-file-code-16: requirements.txt"

    ```
    --8<-- "examples/sqlalchemy-oauth/requirements.txt"
    ```

=== ":octicons-file-code-16: main.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/main.py"
    ```

=== ":octicons-file-code-16: app/app.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/app/app.py"
    ```

=== ":octicons-file-code-16: app/db.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/app/db.py"
    ```

=== ":octicons-file-code-16: app/models.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/app/models.py"
    ```

=== ":octicons-file-code-16: app/users.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/app/users.py"
    ```

#### MongoDB

[Open :octicons-link-external-16:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/mongodb-oauth)

=== ":octicons-file-code-16: requirements.txt"

    ```
    --8<-- "examples/mongodb-oauth/requirements.txt"
    ```

=== ":octicons-file-code-16: main.py"

    ```py
    --8<-- "examples/mongodb-oauth/main.py"
    ```

=== ":octicons-file-code-16: app/app.py"

    ```py
    --8<-- "examples/mongodb-oauth/app/app.py"
    ```

=== ":octicons-file-code-16: app/db.py"

    ```py
    --8<-- "examples/mongodb-oauth/app/db.py"
    ```

=== ":octicons-file-code-16: app/models.py"

    ```py
    --8<-- "examples/mongodb-oauth/app/models.py"
    ```

=== ":octicons-file-code-16: app/users.py"

    ```py
    --8<-- "examples/mongodb-oauth/app/users.py"
    ```

#### Tortoise ORM

[Open :octicons-link-external-16:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/tortoise-oauth)

=== ":octicons-file-code-16: requirements.txt"

    ```
    --8<-- "examples/tortoise-oauth/requirements.txt"
    ```

=== ":octicons-file-code-16: main.py"

    ```py
    --8<-- "examples/tortoise-oauth/main.py"
    ```

=== ":octicons-file-code-16: app/app.py"

    ```py
    --8<-- "examples/tortoise-oauth/app/app.py"
    ```

=== ":octicons-file-code-16: app/db.py"

    ```py
    --8<-- "examples/tortoise-oauth/app/db.py"
    ```

=== ":octicons-file-code-16: app/models.py"

    ```py
    --8<-- "examples/tortoise-oauth/app/models.py"
    ```

=== ":octicons-file-code-16: app/users.py"

    ```py
    --8<-- "examples/tortoise-oauth/app/users.py"
    ```
