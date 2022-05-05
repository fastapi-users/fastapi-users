# Verify router

This router provides routes to manage user email verification. Check the [routes usage](../../usage/routes.md) to learn how to use them.

!!! success "👏👏👏"
    A big thank you to [Edd Salkield](https://github.com/eddsalkield) and [Mark Todd](https://github.com/mark-todd) who worked hard on this feature!

## Setup

```py
import uuid

from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from .db import User
from .schemas import UserRead

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

app = FastAPI()
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
```
