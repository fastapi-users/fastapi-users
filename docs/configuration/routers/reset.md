# Reset password router

The reset password router will generate `/forgot-password` (the user asks for a token to reset its password) and `/reset-password` (the user changes its password given the token) routes.

Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
import uuid

from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from .db import User

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

app = FastAPI()
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
```
