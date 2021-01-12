# 4.x.x ➡️ 5.x.x

## New property `is_verified` in `User` model.

Starting 5.x.x., there is a new [e-mail verification feature](../configuration/routers/verify.md). Even if optional, the `is_verified` property has been added to the `User` model.

If you use **SQLAlchemy** or **Tortoise** databases adapters, you'll have to make a migration to update your database schema.
