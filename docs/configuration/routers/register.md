# Register routes

The register router will generate a `/register` route to allow a user to create a new account.

Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

SECRET = "SECRET"

jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600))

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app = FastAPI()
app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"],
)
```

## After register

You can provide a custom function to be called after a successful registration. It is called with **two argument**: the **user** that has just registered, and the original **`Request` object**.

Typically, you'll want to **send a welcome e-mail** or add it to your marketing analytics pipeline.

You can define it as an `async` or standard method.

Example:

```py
def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")

app.include_router(
    fastapi_users.get_register_router(on_after_register),
    prefix="/auth",
    tags=["auth"],
)
```
