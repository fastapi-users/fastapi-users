# User model

**FastAPI Users** defines a minimal User model for authentication purposes. It is structured like this:

* `id` (`UUID4`) – Unique identifier of the user. Default to a **UUID4**.
* `email` (`str`) – Email of the user. Validated by [`email-validator`](https://github.com/JoshData/python-email-validator).
* `is_active` (`bool`) – Whether or not the user is active. If not, login and forgot password requests will be denied. Default to `True`.
* `is_verified` (`bool`) – Whether or not the user is verified. Optional but helpful with the [`verify` router](./routers/verify.md) logic. Default to `False`.
* `is_superuser` (`bool`) – Whether or not the user is a superuser. Useful to implement administration logic. Default to `False`.

## Define your models

There are four Pydantic models variations provided as mixins:

* `BaseUser`, which provides the basic fields and validation ;
* `BaseCreateUser`, dedicated to user registration, which consists of compulsory `email` and `password` fields ;
* `BaseUpdateUser`, dedicated to user profile update, which adds an optional `password` field ;
* `BaseUserDB`, which is a representation of the user in database, adding a `hashed_password` field.

You should define each of those variations, inheriting from each mixin:

```py
from fastapi_users import models


class User(models.BaseUser):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass
```

You can of course add your own properties there to fit to your needs!

## Password validation

**FastAPI Users** doesn't provide a default password validation, but you can implement it easily with a [Pydantic validator](https://pydantic-docs.helpmanual.io/usage/validators/) on the `UserCreate` class. Here is a simple example to check if the password is at least six characters long:

```py
from fastapi_users import models
from pydantic import validator


class UserCreate(models.BaseUserCreate):
    @validator('password')
    def valid_password(cls, v: str):
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v
```

## Next steps

Depending on your database backend, the database configuration will differ a bit.

[I'm using SQLAlchemy](databases/sqlalchemy.md)

[I'm using MongoDB](databases/mongodb.md)

[I'm using Tortoise ORM](databases/tortoise.md)
