# User model

**FastAPI Users** defines a minimal User model for authentication purposes. It is structured like this:

* `id` (`str`) – Unique identifier of the user. Default to a **UUID4**.
* `email` (`str`) – Email of the user. Validated by [`email-validator`](https://github.com/JoshData/python-email-validator).
* `is_active` (`bool`) – Whether or not the user is active. If not, login and forgot password requests will be denied. Default to `True`.
* `is_active` (`bool`) – Whether or not the user is a superuser. Useful to implement administration logic. Default to `False`.

## Use the model

The model is exposed as a Pydantic model mixin.

```py
from fastapi_users import BaseUser


class User(BaseUser):
    pass
```

You can of course add you own properties there to fit to your needs!

## Next steps

Depending on your database backend, database configuration will differ a bit.

[I'm using SQLAlchemy](databases/sqlalchemy.md)

[I'm using MongoDB](databases/mongodb.md)

[I'm using Tortoise ORM](databases/tortoise.md)
