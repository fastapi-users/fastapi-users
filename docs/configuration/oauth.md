# OAuth2

FastAPI Users provides an optional OAuth2 authentication support. It relies on [HTTPX OAuth library](https://frankie567.github.io/httpx-oauth/), which is a pure-async implementation of OAuth2.

## Installation

You should install the library with the optional dependencies for OAuth:

```sh
pip install 'fastapi-users[sqlalchemy,oauth]'
```

```sh
pip install 'fastapi-users[beanie,oauth]'
```

## Configuration

### Instantiate an OAuth2 client

You first need to get an HTTPX OAuth client instance. [Read the documentation](https://frankie567.github.io/httpx-oauth/oauth2/) for more information.

```py
from httpx_oauth.clients.google import GoogleOAuth2

google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")
```

### Setup the database adapter

#### SQLAlchemy

You'll need to define the SQLAlchemy model for storing OAuth accounts. We provide a base one for this:

```py hl_lines="5 17-18 22 39-40"
--8<-- "docs/src/db_sqlalchemy_oauth.py"
```

Notice that we also manually added a `relationship` on the `UserTable` so that SQLAlchemy can properly retrieve the OAuth accounts of the user.

Besides, when instantiating the database adapter, we need pass this SQLAlchemy model as third argument.

!!! tip "Primary key is defined as UUID"
    By default, we use UUID as a primary key ID for your user. If you want to use another type, like an auto-incremented integer, you can use `SQLAlchemyBaseOAuthAccountTable` as base class and define your own `id` and `user_id` column.

    ```py
    class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
        id = Column(Integer, primary_key=True)

        @declared_attr
        def user_id(cls):
            return Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)

    ```

    Notice that `SQLAlchemyBaseOAuthAccountTable` expects a generic type to define the actual type of ID you use.

#### Beanie

The advantage of MongoDB is that you can easily embed sub-objects in a single document. That's why the configuration for Beanie is quite simple. All we need to do is to define another class to structure an OAuth account object.

```py hl_lines="5 15-16 20"
--8<-- "docs/src/db_beanie_oauth.py"
```

It's worth to note that `OAuthAccount` is **not a Beanie document** but a Pydantic model that we'll embed inside the `User` document, through the `oauth_accounts` array.

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

[Open :material-open-in-new:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/sqlalchemy-oauth)

=== "requirements.txt"

    ```
    --8<-- "examples/sqlalchemy-oauth/requirements.txt"
    ```

=== "main.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/main.py"
    ```

=== "app/app.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/app/app.py"
    ```

=== "app/db.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/app/db.py"
    ```

=== "app/schemas.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/app/schemas.py"
    ```

=== "app/users.py"

    ```py
    --8<-- "examples/sqlalchemy-oauth/app/users.py"
    ```

#### Beanie

[Open :material-open-in-new:](https://github.com/fastapi-users/fastapi-users/tree/master/examples/beanie-oauth)

=== "requirements.txt"

    ```
    --8<-- "examples/beanie-oauth/requirements.txt"
    ```

=== "main.py"

    ```py
    --8<-- "examples/beanie-oauth/main.py"
    ```

=== "app/app.py"

    ```py
    --8<-- "examples/beanie-oauth/app/app.py"
    ```

=== "app/db.py"

    ```py
    --8<-- "examples/beanie-oauth/app/db.py"
    ```

=== "app/schemas.py"

    ```py
    --8<-- "examples/beanie-oauth/app/schemas.py"
    ```

=== "app/users.py"

    ```py
    --8<-- "examples/beanie-oauth/app/users.py"
    ```
