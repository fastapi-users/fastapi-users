# Ormar

**FastAPI Users** provides the necessary tools to work with ormar.

## Installation

Install the database driver that corresponds to your DBMS:

```sh
pip install asyncpg psycopg2
```

```sh
pip install aiomysql pymysql
```

```sh
pip install aiosqlite
```

For the sake of this tutorial from now on, we'll use a simple SQLite databse.

## Setup User table

Let's declare our User ORM model.

```py hl_lines="29-33"
{!./src/db_ormar.py!}
```

As you can see, **FastAPI Users** provides an abstract model that will
include base fields for our User table. You can of course add you own fields
there to fit to your needs!

## Create the database adapter

The database adapter of **FastAPI Users** makes the link between your
database configuration and the users logic. Create it like this.

```py hl_lines="40"
{!./src/db_ormar.py!}
```

Notice that we pass a reference to your [`UserDB` model](../model.md).

!!! warning
    In production, it's strongly recommended to setup a migration system to
    update your SQL schemas. See
    [Alembic](https://alembic.sqlalchemy.org/en/latest/).

## Next steps

We will now configure an [authentication method](../authentication/index.md).
