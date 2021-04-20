# Tortoise ORM

**FastAPI Users** provides the necessary tools to work with Tortoise ORM.

## Installation

Install the database driver that corresponds to your DBMS:

```sh
pip install asyncpg
```

```sh
pip install aiomysql
```

```sh
pip install aiosqlite
```

For the sake of this tutorial from now on, we'll use a simple SQLite databse.

## Setup User table

Let's declare our User ORM model.

```py hl_lines="8 9"
{!./src/db_tortoise.py!}
```

As you can see, **FastAPI Users** provides an abstract model that will include base fields for our User table. You can of course add you own fields there to fit to your needs!

## Tweak `UserDB` model

In order to make the Pydantic model and the Tortoise ORM model working well together, you'll have to add a mixin and some configuration options to your `UserDB` model. Tortoise ORM provides [utilities to ease the integration with Pydantic](https://tortoise-orm.readthedocs.io/en/latest/contrib/pydantic.html) and we'll use them here.

```py hl_lines="5 24 25 26 27"
{!./src/db_tortoise.py!}
```

The `PydanticModel` mixin adds methods used internally by Tortoise ORM to the Pydantic model so that it can easily transform it back to an ORM model. It expects then that you provide the property `orig_model` which should point to the **User ORM model we defined just above**.

## Create the database adapter

The database adapter of **FastAPI Users** makes the link between your database configuration and the users logic. Create it like this.

```py hl_lines="32"
{!./src/db_tortoise.py!}
```

Notice that we pass a reference to your [`UserDB` model](../model.md).

## Register Tortoise

For using Tortoise ORM we must register our models and database.

Tortoise ORM supports integration with FastAPI out-of-the-box. It will automatically bind startup and shutdown events.

```py hl_lines="35 36 37 38 39 40"
{!./src/db_tortoise.py!}
```

!!! warning
    In production, it's strongly recommended to setup a migration system to update your SQL schemas. See [https://tortoise-orm.readthedocs.io/en/latest/migration.html](https://tortoise-orm.readthedocs.io/en/latest/migration.html).

## Next steps

We will now configure an [authentication method](../authentication/index.md).
