# Routers

We're almost there! The last step is to configure the `FastAPIUsers` object that will wire the database adapter, the authentication classes and let us generate the actual **API routes**.

## Configure `FastAPIUsers`

Configure `FastAPIUsers` object with all the elements we defined before. More precisely:

* `db`: Database adapter instance.
* `auth_backends`: List of authentication backends. See [Authentication](../authentication/index.md).
* `user_model`: Pydantic model of a user.
* `user_create_model`: Pydantic model for creating a user.
* `user_update_model`: Pydantic model for updating a user.
* `user_db_model`: Pydantic model of a DB representation of a user.

```py
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
```

## Available routers

This helper class will let you generate useful routers to setup the authentication system. Each of them is **optional**, so you can pick only the one that you are interested in! Here are the routers provided:

* [Auth router](./auth.md): Provides `/login` and `/logout` routes for a given [authentication backend](../authentication/index.md).
* [Register router](./register.md): Provides `/register` routes to allow a user to create a new account.
* [Reset password router](./reset.md): Provides `/forgot-password` and `/reset-password` routes to allow a user to reset its password.
* [Verify router](./verify.md): Provides `/request-verify-token` and `/verify` routes to manage user e-mail verification.
* [Users router](./users.md): Provides routes to manage users.
* [OAuth router](../oauth.md): Provides routes to perform an OAuth authentication against a service provider (like Google or Facebook).

You should check out each of them to understand how to use them.
