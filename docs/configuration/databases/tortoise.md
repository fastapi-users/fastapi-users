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

```py hl_lines="26 27"
{!./src/db_tortoise.py!}
```

As you can see, **FastAPI Users** provides an abstract model that will include base fields for our User table. You can of course add you own fields there to fit to your needs!

## Create the database adapter

The database adapter of **FastAPI Users** makes the link between your database configuration and the users logic. Create it like this.

```py hl_lines="30"
{!./src/db_tortoise.py!}
```

Notice that we pass a reference to your [`UserDB` model](../model.md).

## Register Tortoise

For using Tortoise ORM we must register our models and database.

Tortoise ORM supports integration with Starlette/FastAPI out-of-the-box. It will automatically bind startup and shutdown events.

```py hl_lines="33"
{!./src/db_tortoise.py!}
```

## Next steps

We will now configure an [authentication method](../authentication/index.md).
