# MongoDB

**FastAPI Users** provides the necessary tools to work with Tortoise ORM.

## Installation

Install the Tortoise ORM and needed DB driver.

```sh
pip install tortoise-orm
```

```sh
pip install asyncpg  # or any another async db driver
```

For the sake of this tutorial from now on, we'll use a simple SQLite databse.

## Setup User table

Let's declare our User table.

```py hl_lines="7 8 9"
{!./src/db_tortoise.py!}
```

As you can see, **FastAPI Users** provides a mixin that will include base fields for our User table. You can of course add you own fields there to fit to your needs!

## Create the database adapter

The database adapter of **FastAPI Users** makes the link between your database configuration and the users logic. Create it like this.

```py hl_lines="11"
{!./src/db_tortoise.py!}
```

## Register Tortoise

For using Tortoise ORM we must register our models and database.

Tortoise ORM supports integration with Starlette (FastAPI based on Starlette) and we can use it.

```py hl_lines="14"
{!./src/db_tortoise.py!}
```


## Next steps

We will now configure an [authentication method](../authentication/index.md).
