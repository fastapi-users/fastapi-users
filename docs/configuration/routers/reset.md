# Reset password router

The reset password router will generate `/forgot-password` (the user asks for a token to reset its password) and `/reset-password` (the user changes its password given the token) routes.

Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers

SECRET = "SECRET"

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app = FastAPI()
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
```
