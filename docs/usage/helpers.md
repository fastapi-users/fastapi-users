# Helpers

**FastAPI Users** provides some helper functions to perform some actions programmatically. They are available from your `FastAPIUsers` instance.

## Create user

Create a user.

```py
regular_user = await fastapi_users.create_user(
    UserCreate(
        email="king.arthur@camelot.bt",
        password="guinevere",
    )
)

superuser = await fastapi_users.create_user(
    UserCreate(
        email="king.arthur@camelot.bt",
        password="guinevere",
        is_superuser=True,
    )
)
```

## Verify user

Verify a user.

```py
verified_user = await fastapi_users.verify_user(non_verified_user)
assert verified_user.is_verified is True
```

## Get user

Retrieve a user by e-mail.

```py
user = await fastapi_users.get_user("king.arthur@camelot.bt")
```
