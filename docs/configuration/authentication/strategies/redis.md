# Redis

[Redis](https://redis.io/) is an ultra-fast key-store database. As such, it's a good candidate for token management. In this strategy, a token is generated and associated with the user id. in the database. On each request, we try to retrieve this token from Redis to get the corresponding user id.

## Configuration

```py
import aioredis
from fastapi_users.authentication import RedisStrategy

redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)

def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)
```

As you can see, instantiation is quite simple. It accepts the following arguments:

* `redis` (`aioredis.Redis`): An instance of `aioredis.Redis`. Note that the `decode_responses` flag set to `True` is necessary.
* `lifetime_seconds` (`Optional[int]`): The lifetime of the token in seconds. Defaults to `None`, which means the token doesn't expire.

!!! tip "Why it's inside a function?"
    To allow strategies to be instantiated dynamically with other dependencies, they have to be provided as a callable to the authentication backend.

## Logout

On logout, this strategy will delete the token from the Redis store.
