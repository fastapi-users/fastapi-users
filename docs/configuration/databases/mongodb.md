# MongoDB

**FastAPI Users** provides the necessary tools to work with MongoDB databases thanks to [mongodb/motor](https://github.com/mongodb/motor) package for full async support.

## Setup database connection and collection

Let's create a MongoDB connection and instantiate a collection.

```py hl_lines="5 6 7 8"
{!./src/db_mongodb.py!}
```

You can choose any name for the database and the collection.

## Create the database adapter

The database adapter of **FastAPI Users** makes the link between your database configuration and the users logic. Create it like this.

```py hl_lines="14"
{!./src/db_mongodb.py!}
```

!!! info
    The database adapter will automatically create a [unique index](https://docs.mongodb.com/manual/core/index-unique/) on `id` and `email`.

!!! warning
    **FastAPI Users** will use its defined [`id` UUID-string](../model.md) as unique identifier for the user, rather than the builtin MongoDB `_id`.

## Next steps

We will now configure an [authentication method](../authentication/index.md).
