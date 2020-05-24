# Reset password router

The reset password router will generate `/forgot-password` (the user asks for a token to reset its password) and `/reset-password` (the user changes its password given the token) routes.

Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app = FastAPI()
app.include_router(
    fastapi_users.get_reset_password_router("SECRET"),
    prefix="/auth",
    tags=["auth"],
)
```

Parameters:

* `reset_password_token_secret`: Secret to encode reset password token.
* `reset_password_token_lifetime_seconds`: Lifetime of reset password token. **Defaults to 3600**.
* `after_forgot_password`: Optional function called after a successful forgot password request. See below.

## After forgot password

You can provide a custom function to be called after a successful forgot password request. It is called with **three arguments**:

* The **user** which has requested to reset their password.
* A ready-to-use **JWT token** that will be accepted by the reset password route.
* The original **`Request` object**.

Typically, you'll want to **send an e-mail** with the link (and the token) that allows the user to reset their password.

You can define it as an `async` or standard method.

Example:

```py
def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")

app.include_router(
    fastapi_users.get_reset_password_router("SECRET", after_forgot_password=on_after_forgot_password),
    prefix="/auth",
    tags=["auth"],
)
```
