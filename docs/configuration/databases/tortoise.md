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

Let's declare our User model.

```py hl_lines="9 10"
{!./src/db_tortoise.py!}
```

As you can see, **FastAPI Users** provides a mixin that will include base fields for our User table. You can of course add you own fields there to fit to your needs!

## Create the database adapter

The database adapter of **FastAPI Users** makes the link between your database configuration and the users logic. Create it like this.

```py hl_lines="13"
{!./src/db_tortoise.py!}
```

## Register Tortoise

For using Tortoise ORM we must register our models and database.

Tortoise ORM supports integration with Starlette/FastAPI out-of-the-box. It will automatically bind startup and shutdown events.

```py hl_lines="16"
{!./src/db_tortoise.py!}
```

## Next steps

We will now configure an [authentication method](../authentication/index.md).
