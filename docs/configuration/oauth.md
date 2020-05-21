# OAuth2

FastAPI Users provides an optional OAuth2 authentication support. It relies on [HTTPX OAuth library](https://frankie567.github.io/httpx-oauth/), which is a pure-async implementation of OAuth2.

## Installation

You should install the library with the optional dependencies for OAuth:

```sh
pip install fastapi-users[sqlalchemy,oauth]
```

```sh
pip install fastapi-users[mongodb,oauth]
```

```sh
pip install fastapi-users[tortoise-orm,oauth]
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


class UserCreate(User, models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass
```

Notice that we inherit from the `BaseOAuthAccountMixin`, which adds a `List` of `BaseOAuthAccount` objects. This object is structured like this:

* `id` (`UUID4`) – Unique identifier of the OAuth account information. Default to a **UUID4**.
* `oauth_name` (`str`) – Name of the OAuth service. It corresponds to the `name` property of the OAuth client.
* `access_token` (`str`) – Access token.
* `expires_at` (`int`) - Timestamp at which the access token is expired.
* `refresh_token` (`Optional[str]`) – On services that support it, a token to get a fresh access token.
* `account_id` (`str`) - Identifier of the OAuth account on the corresponding service.
* `account_email` (`str`) - Email address of the OAuth account on the corresponding service.

### Setup the database adapter

#### SQLAlchemy

You'll need to define the table for storing the OAuth account model. We provide a base one for this:

```py
from fastapi_users.db.sqlalchemy import SQLAlchemyBaseOAuthAccountTable

class OAuthAccount(SQLAlchemyBaseOAuthAccountTable, Base):
    pass
```

Then, you should declare it on the database adapter:

```py
user_db = SQLAlchemyUserDatabase(UserDB, database, User.__table__, OAuthAccount.__table__)
```

#### MongoDB

Nothing to do, the [basic configuration](./databases/mongodb.md) is enough.

#### Tortoise ORM

You'll need to define the Tortoise model for storing the OAuth account model. We provide a base one for this:

```py
from fastapi_users.db.tortoise import TortoiseBaseOAuthAccountModel


class OAuthAccount(TortoiseBaseOAuthAccountModel):
    user = fields.ForeignKeyField("models.User", related_name="oauth_accounts")
```

!!! warning
    Note that you should define the foreign key yourself, so that you can point it the user model in your namespace.

Then, you should declare it on the database adapter:

```py
user_db = TortoiseUserDatabase(UserDB, User, OAuthAccount)
```

### Generate a router

Once you have a `FastAPIUsers` instance, you can make it generate a single OAuth router for the given client.

```py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers
from httpx_oauth.clients.google import GoogleOAuth2

google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")

app = FastAPI()
fastapi_users = FastAPIUsers(
    user_db, auth_backends, User, UserCreate, UserUpdate, UserDB, SECRET,
)

google_oauth_router = fastapi_users.get_oauth_router(google_oauth_client, SECRET)

app.include_router(google_oauth_router, prefix="/google-oauth", tags=["users"])
```

### Full example

``` py tab="SQLAlchemy"
{!./src/oauth_full_sqlalchemy.py!}
```

```py tab="MongoDB"
{!./src/oauth_full_mongodb.py!}
```

```py tab="Tortoise ORM"
{!./src/oauth_full_tortoise.py!}
```
