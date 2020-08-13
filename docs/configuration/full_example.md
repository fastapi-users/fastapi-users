# Full example

Here is a full working example with JWT authentication to help get you started.

!!! warning
    Notice that **SECRET** should be changed to a strong passphrase.
    Insecure passwords may give attackers full access to your database.

## SQLAlchemy

```py
{!./src/full_sqlalchemy.py!}
```

## MongoDB

```py
{!./src/full_mongodb.py!}
```

## Tortoise ORM

```py
{!./src/full_tortoise.py!}
```

## What now?

You're ready to go! Be sure to check the [Usage](../usage/routes.md) section to understand how yo work with **FastAPI Users**.
