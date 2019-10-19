# SQLAlchemy

**FastAPI Users** provides the necessary tools to work with SQL databases thanks to [SQLAlchemy Core](https://docs.sqlalchemy.org/en/13/core/) and [encode/databases](https://www.encode.io/databases/) package for full async support.

## Installation

Install the database driver that corresponds to your DBMS:

```sh
pip install databases[postgresql]
```

```sh
pip install databases[mysql]
```

```sh
pip install databases[sqlite]
```

For the sake of this tutorial from now on, we'll use a simple SQLite databse.

## Setup User table

Let's create a `metadata` object and declare our User table.

```py hl_lines="4 14 15"
{!./src/sqlalchemy.py!}
```

As you can see, **FastAPI Users** provides a mixin that will include base fields for our User table. You can of course add you own fields there to fit to your needs!

## Create the tables

We'll now create an SQLAlchemy enigne and ask it to create all the defined tables.

```py hl_lines="18 19 20 21 22"
{!./src/sqlalchemy.py!}
```

!!!tip
    In production, you would probably want to create the tables with Alembic, integrated with migrations, etc.

## Create the database adapter

The database adapter of **FastAPI Users** makes the link between your database configuration and the users logic. Create it like this.

```py hl_lines="24 25"
{!./src/sqlalchemy.py!}
```

Notice that we declare the `users` variable, which is the actual SQLAlchemy table behind the table class. We also use our `database` instance, which allows us to do asynchronous request to the database.

{!./configuration/authentication/_next_authentication.md!}

## What about SQLAlchemy ORM?

The primary objective was to use pure async approach as much as possible. However, we understand that ORM is convenient and useful for many developers. If this feature becomes very demanded, we will add a database adapter for SQLAlchemy ORM.
