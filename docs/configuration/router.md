# Router

We're almost there! The last step is to configure the `FastAPIUsers` object that will wire the database adapter, the authentication class and the user model to expose the FastAPI router.

## Configure `FastAPIUsers`

Configure `FastAPIUsers` object with all the elements we defined before. More precisely:

* `db`: Database adapter instance.
* `auth`: Authentication logic instance.
* `user_model`: Pydantic model of a user.
* `reset_password_token_secret`: Secret to encode reset password token.
* `reset_password_token_lifetime_seconds`: Lifetime of reset password token in seconds. Default to one hour.

```py
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers(
    user_db,
    auth,
    User,
    SECRET,
)
```

And then, include the router in the FastAPI app:

```py
app = FastAPI()
app.include_router(fastapi_users.router, prefix="/users", tags=["users"])
```

## Event handlers

In order to be as unopinionated as possible, we expose decorators that allow you to plug your own logic after some actions. You can have several handlers per event.

### After forgot password

This event handler is called after a successful forgot password request. It is called with **two arguments**: the **user** which has requested to reset their password and a ready-to-use **JWT token** that will be accepted by the reset password route.

Typically, you'll want to **send an e-mail** with the link (and the token) that allows the user to reset their password.

You can define it as an `async` or standard method.

Example:

```py
@fastapi_users.on_after_forgot_password()
def on_after_forgot_password(user, token):
    print(f'User {user.id} has forgot their password. Reset token: {token}')
```

## Next steps

Check out a [full example](full_example.md) that will show you the big picture.
