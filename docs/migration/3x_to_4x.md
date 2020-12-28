# 3.x.x ➡️ 4.x.x

## `expires_at` property in `OAuthAccount` is now optional

Before 4.x.x, the `expires_at` property in `OAuthAccount` model was mandatory. It was causing issues with some services that don't have such expiration property.

If you use **SQLAlchemy** or **Tortoise** databases adapters, you'll have to make a migration to update your database schema.
