# Models

**FastAPI Users** defines a minimal User model for authentication purposes. It is structured like this:

* `id` (`UUID4`) – Unique identifier of the user. Defaults to a **UUID4**.
* `email` (`str`) – Email of the user. Validated by [`email-validator`](https://github.com/JoshData/python-email-validator).
* `is_active` (`bool`) – Whether or not the user is active. If not, login and forgot password requests will be denied. Defaults to `True`.
* `is_verified` (`bool`) – Whether or not the user is verified. Optional but helpful with the [`verify` router](./routers/verify.md) logic. Defaults to `False`.
* `is_superuser` (`bool`) – Whether or not the user is a superuser. Useful to implement administration logic. Defaults to `False`.

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


class UserUpdate(models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass
```

### Adding your own fields

You can of course add your own properties there to fit to your needs. In the example below, we add a required string property, `first_name`, and an optional date property, `birthdate`.

```py
import datetime

from fastapi_users import models


class User(models.BaseUser):
    first_name: str
    birthdate: Optional[datetime.date]


class UserCreate(models.BaseUserCreate):
    first_name: str
    birthdate: Optional[datetime.date]


class UserUpdate(models.BaseUserUpdate):
    first_name: Optional[str]
    birthdate: Optional[datetime.date]


class UserDB(User, models.BaseUserDB):
    pass
```
