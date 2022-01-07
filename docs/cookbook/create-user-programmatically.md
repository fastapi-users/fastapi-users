# Create a user programmatically

Sometimes, you'll need to create a user programmatically in the code rather than passing by the REST API endpoint. To do this, we'll create a function that you can call from your code.

In this context, we are outside the dependency injection mechanism of FastAPI, so we have to take care of instantiating the [`UserManager` class](../configuration/user-manager.md) and all other dependent objects **manually**.

For this cookbook, we'll consider you are starting from the [SQLAlchemy full example](../configuration/full-example.md), but it'll be rather similar for other DBMS.

## 1. Define dependencies as context managers

Generally, FastAPI dependencies are defined as **generators**, using the `yield` keyword. FastAPI knows very well to handle them inside its dependency injection system. For example, here is the definition of the `get_user_manager` dependency:

```py
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
  yield UserManager(user_db)
```

In Python, when we want to use a generator, we have to use a `for` loop, which would be a bit unnatural in this context since we have only one value to get, the user manager instance. To avoid this, we'll transform them into **context managers**, so we can call them using the `with..as` syntax. Fortunately, the standard library provides tools to automatically transform generators into context managers.

In the following sample, we import our dependencies and create a context manager version using `contextlib.asynccontextmanager`:

```py hl_lines="8-10"
--8<-- "docs/src/cookbook_create_user_programmatically.py"
```

!!! info "I have other dependencies"
    Since FastAPI Users fully embraces dependency injection, you may have more arguments passed to your database or user manager dependencies. It's important then to not forget anyone. Once again, outside the dependency injection system, you are responsible of instantiating **everything** yourself.

## 2. Write a function

We are now ready to write a function. The example below shows you a basic example but you can of course adapt it to your own needs. The key part here is once again to **take care of opening every context managers and pass them every required arguments**, as the dependency manager would do.

```py hl_lines="13-25"
--8<-- "docs/src/cookbook_create_user_programmatically.py"
```

## 3. Use it

You can now easily use it in a script. For example:

```py
import asyncio

if __name__ == "__main__":
  asyncio.run(create_user("king.arthur@camelot.bt", "guinevere"))
```
