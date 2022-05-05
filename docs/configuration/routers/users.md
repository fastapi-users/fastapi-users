# Users router

This router provides routes to manage users. Check the [routes usage](../../usage/routes.md) to learn how to use them.

## Setup

```py
import uuid

from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from .db import User
from .schemas import UserRead, UserUpdate

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

app = FastAPI()
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
```

### Optional: user verification

You can require the user to be **verified** (i.e. `is_verified` property set to `True`) to access those routes. You have to set the `requires_verification` parameter to `True` on the router instantiation method:

```py
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)
```
