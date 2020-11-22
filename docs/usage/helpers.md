# Helpers

## Create user

**FastAPI Users** provides a helper function to easily create a user programmatically. They are available from your `FastAPIUsers` instance.

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
