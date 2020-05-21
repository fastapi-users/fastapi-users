# MongoDB

**FastAPI Users** provides the necessary tools to work with MongoDB databases thanks to [mongodb/motor](https://github.com/mongodb/motor) package for full async support.

## Setup database connection and collection

Let's create a MongoDB connection and instantiate a collection.

```py hl_lines="23 24 25 26"
{!./src/db_mongodb.py!}
```

You can choose any name for the database and the collection.

!!! warning
    You may have noticed the `uuidRepresentation` parameter. It controls how the UUID values will be encoded in the database. By default, it's set to `pythonLegacy` but new applications should consider setting this to `standard` for cross language compatibility. [Read more about this](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient).

## Create the database adapter

The database adapter of **FastAPI Users** makes the link between your database configuration and the users logic. Create it like this.

```py hl_lines="34"
{!./src/db_mongodb.py!}
```

Notice that we pass a reference to your [`UserDB` model](../model.md).

!!! info
    The database adapter will automatically create a [unique index](https://docs.mongodb.com/manual/core/index-unique/) on `id` and `email`.

!!! warning
    **FastAPI Users** will use its defined [`id` UUID](../model.md) as unique identifier for the user, rather than the builtin MongoDB `_id`.

## Next steps

We will now configure an [authentication method](../authentication/index.md).
