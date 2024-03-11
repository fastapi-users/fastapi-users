# Password hash

By default, FastAPI Users will use the [Argon2 algorithm](https://en.wikipedia.org/wiki/Argon2) to **hash and salt** passwords before storing them in the database, with backwards-compatibility with [Bcrypt](https://en.wikipedia.org/wiki/Bcrypt).

The implementation is provided by [pwdlib](https://github.com/frankie567/pwdlib), a modern password hashing wrapper.

## Customize `PasswordHash`

If you need to tune the algorithms used or their settings, you can customize the [`PasswordHash` object of pwdlib](https://frankie567.github.io/pwdlib/reference/pwdlib/#pwdlib.PasswordHash).

For this, you'll need to instantiate the `PasswordHelper` class and pass it your `PasswordHash`. The example below shows you how you can create a `PasswordHash` to only support the Argon2 algorithm.

```py
from fastapi_users.password import PasswordHelper
from pwdlib import PasswordHash, exceptions
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((
    Argon2Hasher(),
))
password_helper = PasswordHelper(password_hash)
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

## Full customization

If you don't wish to use `pwdlib` at all – **which we don't recommend unless you're absolutely sure of what you're doing** — you can implement your own `PasswordHelper` class as long as it implements the `PasswordHelperProtocol` and its methods.

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
