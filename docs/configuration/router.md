# Router

We're almost there! The last step is to configure the `FastAPIUsers` object that will wire the database adapter, the authentication class and the user model to expose the FastAPI router.

## Hooks

In order to be as unopinionated as possible, you'll have to define your logic after some actions.

### After forgot password

This hook is called after a successful forgot password request. It is called with **two arguments**: the **user** which has requested to reset their password and a ready-to-use **JWT token** that will be accepted by the reset password route.

Typically, you'll want to **send an e-mail** with the link (and the token) that allows the user to reset their password.

You can define it as an `async` or standard method.

Example:

```py
def on_after_forgot_password(user, token):
    print(f'User {user.id} has forgot their password. Reset token: {token}')
```

## Configure `FastAPIUsers`

The last step is to instantiate `FastAPIUsers` object with all the elements we defined before. More precisely:

* `db`: Database adapter instance.
* `auth`: Authentication logic instance.
* `user_model`: Pydantic model of a user.
* `on_after_forgot_password`: Hook called after a forgot password request.
* `reset_password_token_secret`: Secret to encode reset password token.
* `reset_password_token_lifetime_seconds`: Lifetime of reset password token in seconds. Default to one hour.

```py
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers(
    user_db,
    auth,
    User,
    on_after_forgot_password,
    SECRET,
)
```

And then, include the router in the FastAPI app:

```py
app = FastAPI()
app.include_router(fastapi_users.router, prefix="/users", tags=["users"])
```

## Next steps

Check out a [full example](full_example.md) that will show you the big picture.
