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

```py hl_lines="5 19-20 24-26 43-44"
--8<-- "docs/src/db_sqlalchemy_oauth.py"
```

Notice that we also manually added a `relationship` on `User` so that SQLAlchemy can properly retrieve the OAuth accounts of the user.

Besides, when instantiating the database adapter, we need pass this SQLAlchemy model as third argument.

!!! tip "Primary key is defined as UUID"
    By default, we use UUID as a primary key ID for your user. If you want to use another type, like an auto-incremented integer, you can use `SQLAlchemyBaseOAuthAccountTable` as base class and define your own `id` and `user_id` column.

    ```py
    class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
        id: Mapped[int] = mapped_column(Integer, primary_key=True)

        @declared_attr
        def user_id(cls) -> Mapped[int]:
            return mapped_column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)

    ```

    Notice that `SQLAlchemyBaseOAuthAccountTable` expects a generic type to define the actual type of ID you use.

#### Beanie

The advantage of MongoDB is that you can easily embed sub-objects in a single document. That's why the configuration for Beanie is quite simple. All we need to do is to define another class to structure an OAuth account object.

```py hl_lines="5 15-16 20"
--8<-- "docs/src/db_beanie_oauth.py"
```

It's worth to note that `OAuthAccount` is **not a Beanie document** but a Pydantic model that we'll embed inside the `User` document, through the `oauth_accounts` array.

### Generate routers

Once you have a `FastAPIUsers` instance, you can make it generate a single OAuth router for a given client **and** authentication backend.

```py
app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, "SECRET"),
    prefix="/auth/google",
    tags=["auth"],
)
```

!!! tip
    If you have several OAuth clients and/or several authentication backends, you'll need to create a router for each pair you want to support.

#### Existing account association

If a user with the same e-mail address already exists, an HTTP 400 error will be raised by default.

You can however choose to automatically link this OAuth account to the existing user account by setting the `associate_by_email` flag:

```py
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        "SECRET",
        associate_by_email=True,
    ),
    prefix="/auth/google",
    tags=["auth"],
)
```

Bear in mind though that it can lead to security breaches if the OAuth provider does not validate e-mail addresses. How?

* Let's say your app support an OAuth provider, *Merlinbook*, which does not validate e-mail addresses.
* Imagine a user registers to your app with the e-mail address `lancelot@camelot.bt`.
* Now, a malicious user creates an account on *Merlinbook* with the same e-mail address. Without e-mail validation, the malicious user can use this account without limitation.
* The malicious user authenticates using *Merlinbook* OAuth on your app, which automatically associates to the existing `lancelot@camelot.bt`.
* Now, the malicious user has full access to the user account on your app 😞

#### Association router for authenticated users

We also provide a router to associate an already authenticated user with an OAuth account. After this association, the user will be able to authenticate with this OAuth provider.

```py
app.include_router(
    fastapi_users.get_oauth_associate_router(google_oauth_client, UserRead, "SECRET"),
    prefix="/auth/associate/google",
    tags=["auth"],
)
```

Notice that, just like for the [Users router](./routers/users.md), you have to pass the `UserRead` Pydantic schema.

#### Set `is_verified` to `True` by default

!!! tip "This section is only useful if you set up email verification"
    You can read more about this feature [here](./routers/verify.md).

When a new user registers with an OAuth provider, the `is_verified` flag is set to `False`, which requires the user to verify its email address.

You can choose to trust the email address given by the OAuth provider and set the `is_verified` flag to `True` after registration. You can do this by setting the `is_verified_by_default` argument:

```py
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        "SECRET",
        is_verified_by_default=True,
    ),
    prefix="/auth/google",
    tags=["auth"],
)
```

!!! danger "Make sure you can trust the OAuth provider"
    Make sure the OAuth provider you're using **does verify** the email address before enabling this flag.

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
