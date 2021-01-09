# Verify router

This router provides routes to manage user email verification. Check the [routes usage](../../usage/routes.md) to learn how to use them.

!!! success "👏👏👏"
    A big thank you to [Edd Salkield](https://github.com/eddsalkield) and [Mark Todd](https://github.com/mark-todd) who worked hard on this feature!

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
    fastapi_users.get_verify_router("SECRET"),
    prefix="/auth",
    tags=["auth"],
)
```

Parameters:

* `verification_token_secret`: Secret to encode verify token.
* `verification_token_lifetime_seconds`: Lifetime of verify token. **Defaults to 3600**.
* `after_verification_request`: Optional function called after a successful verify request. See below.
* `after_verification`: Optional function called after a successful verification. See below.

## After verification request

You can provide a custom function to be called after a successful verification request. It is called with **three arguments**:

* The **user** for which the verification has been requested.
* A ready-to-use **JWT token** that will be accepted by the verify route.
* The original **`Request` object**.

Typically, you'll want to **send an e-mail** with the link (and the token) that allows the user to verify their e-mail.

You can define it as an `async` or standard method.

Example:

```py
def after_verification_request(user: UserDB, token: str, request: Request):
    print(f"Verification requested for user {user.id}. Verification token: {token}")

app.include_router(
    fastapi_users.get_verify_router("SECRET", after_verification_request=after_verification_request),
    prefix="/auth",
    tags=["auth"],
)
```

## After verification

You can provide a custom function to be called after a successful user verification. It is called with **two arguments**:

* The **user** that has been verified.
* The original **`Request` object**.

This may be useful if you wish to send another e-mail or store this information in a data analytics or customer success platform.

You can define it as an `async` or standard method.

Example:

```py
def after_verification(user: UserDB, request: Request):
    print(f"{user.id} is now verified.")

app.include_router(
    fastapi_users.get_verify_router("SECRET", after_verification=after_verification),
    prefix="/auth",
    tags=["auth"],
)
```
