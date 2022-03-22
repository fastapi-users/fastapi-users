# Password hash

By default, FastAPI Users will use the [BCrypt algorithm](https://en.wikipedia.org/wiki/Bcrypt) to **hash and salt** passwords before storing them in the database.

The implementation is provided by [Passlib](https://passlib.readthedocs.io/en/stable/index.html), a battle-tested Python library for password hashing.

## Customize `CryptContext`

If you need to support other hashing algorithms, you can customize the [`CryptContext` object of Passlib](https://passlib.readthedocs.io/en/stable/lib/passlib.context.html#the-cryptcontext-class).

For this, you'll need to instantiate the `PasswordHelper` class and pass it your `CryptContext`. The example below shows you how you can create a `CryptContext` to add support for the Argon2 algorithm while deprecating BCrypt.

```py
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext

context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
password_helper = PasswordHelper(context)
```

Finally, pass the `password_helper` variable while instantiating your `UserManager`:

```py
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db, password_helper)
```

!!! info "Password hashes are automatically upgraded"
    FastAPI Users takes care of upgrading the password hash to a more recent algorithm when needed.

    Typically, when a user logs in, we'll check if the password hash algorithm is deprecated.

    If it is, we take the opportunity of having the password in plain-text at hand (since the user just logged in!) to hash it with a better algorithm and update it in database.

!!! warning "Dependencies for alternative algorithms are not included by default"
    FastAPI Users won't install required dependencies to make other algorithms like Argon2 work. It's up to you to install them.

## Full customization

If you don't wist to use Passlib at all – **which we don't recommend unless you're absolutely sure of what you're doing** — you can implement your own `PasswordHelper` class as long as it implements the `PasswordHelperProtocol` and its methods.

```py
from typing import Tuple

from fastapi_users.password import PasswordHelperProtocol

class PasswordHelper(PasswordHelperProtocol):
    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> Tuple[bool, str]:
        ...

    def hash(self, password: str) -> str:
        ...

    def generate(self) -> str:
        ...
```
