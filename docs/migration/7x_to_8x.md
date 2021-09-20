# 7.x.x ➡️ 8.x.x

Version 8 includes the biggest code changes since version 1. We reorganized lot of parts of the code to make it even more modular and integrate more into the dependency injection system of FastAPI.

Most importantly, you need now to implement a `UserManager` class and a associated dependency to create an instance of this class.

## Event handlers should live in the `UserManager`

Before, event handlers like `on_after_register` or `on_after_forgot_password` were defined in their own functions that were passed as arguments of router generators.

Now, they should be **methods** of the `UserManager` class.

You can read more in the [`UserManager` documentation](../configuration/user-manager.md).

## Password validation should live in the `UserManager`

Before, password validation was defined in its own function that was passed as argument of `FastAPIUsers`.

Now, it should be a method of the `UserManager` class.

You can read more in the [`UserManager` documentation](../configuration/user-manager.md).

## Verify token secret and lifetime parameters are attributes of `UserManager`

Before, verify token and lifetime parameters were passed as argument of `get_verify_router`.

Now, they should be defined as attributes of the `UserManager` class.

You can read more in the [`UserManager` documentation](../configuration/user-manager.md).

## Reset password token secret and lifetime parameters are attributes of `UserManager`

Before, reset password token and lifetime parameters were passed as argument of `get_verify_router`.

Now, they should be defined as attributes of the `UserManager` class.

You can read more in the [`UserManager` documentation](../configuration/user-manager.md).

## Database adapter should be provided in a dependency

Before, we advised to directly instantiate the database adapter class.

Now, it should be instantiated inside a dependency that you define yourself. The benefit of this is that it lives in the dependency injection system of FastAPI, allowing you to have more dynamic logic to create your instance.


➡️ [I'm using SQLAlchemy](../configuration/databases/sqlalchemy.md)

➡️ [I'm using MongoDB](../configuration/databases/mongodb.md)

➡️ [I'm using Tortoise ORM](../configuration/databases/tortoise.md)

➡️ [I'm using ormar](../configuration/databases/ormar.md)

## FastAPIUsers now expect a `get_user_manager` dependency

Before, the database adapter instance was passed as argument of `FastAPIUsers`.

Now, you should define a `get_user_manager` dependency returning an instance of your `UserManager` class. This dependency will be dependent of the database adapter dependency.


You can read more in the [`UserManager` documentation](../configuration/user-manager.md) and [`FastAPIUsers` documentation](http://localhost:8000/configuration/routers/)

## Lost?

If you're unsure or a bit lost, make sure to check the [full working examples](../configuration/full-example.md).
