# UserManager

The `UserManager` class is the core logic of FastAPI Users. We provide the `BaseUserManager` class which you should extend to set some parameters and define logic, for example when a user just registered or forgot its password.

It's designed to be easily extensible and customizable so that you can integrate less generic logic.

## Create your `UserManager` class

You should define your own version of the `UserManager` class to set various parameters.

```py hl_lines="12-28"
--8<-- "docs/src/user_manager.py"
```

As you can see, you have to define here various attributes and methods. You can find the complete list of those below.

## Create `get_user_manager` dependency

The `UserManager` class will be injected at runtime using a FastAPI dependency. This way, you can run it in a database session or swap it with a mock during testing.

```py hl_lines="31-32"
--8<-- "docs/src/user_manager.py"
```

Notice that we use the `get_user_db` dependency we defined earlier to inject the database instance.

## Customize attributes and methods

### Attributes

* `user_db_model`: Pydantic model of a DB representation of a user.
* `reset_password_token_secret`: Secret to encode reset password token. **Use a strong passphrase and keep it secure.**
* `reset_password_token_lifetime_seconds`: Lifetime of reset password token. Defaults to 3600.
* `reset_password_token_audience`: JWT audience of reset password token. Defaults to `fastapi-users:reset`.
* `verification_token_secret`: Secret to encode verification token. **Use a strong passphrase and keep it secure.**
* `verification_token_lifetime_seconds`: Lifetime of verification token. Defaults to 3600.
* `verification_token_audience`: JWT audience of verification token. Defaults to `fastapi-users:verify`.

### Methods

#### `validate_password`

Validate a password.

**Arguments**

* `password` (`str`): the password to validate.
* `user` (`Union[UserCreate, User]`): user model which we are currently validating the password. Useful if you want to check that the password doesn't contain the name or the birthdate of the user for example.

**Output**

This function should return `None` if the password is valid or raise `InvalidPasswordException` if not. This exception expects an argument `reason` telling why the password is invalid. It'll be part of the error response.

**Example**

```py
from fastapi_users import BaseUserManager, InvalidPasswordException


class UserManager(BaseUserManager[UserCreate, UserDB]):
    # ...
    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, UserDB],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )
```

#### `on_after_register`

Perform logic after successful user registration.

Typically, you'll want to **send a welcome e-mail** or add it to your marketing analytics pipeline.

**Arguments**

* `user` (`UserDB`): the registered user.
* `request` (`Optional[Request]`): optional FastAPI request object that triggered the operation. Defaults to None.

**Example**

```py
from fastapi_users import BaseUserManager


class UserManager(BaseUserManager[UserCreate, UserDB]):
    # ...
    async def on_after_register(self, user: UserDB, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
```

#### `on_after_update`

Perform logic after successful user update.

It may be useful, for example, if you wish to update your user in a data analytics or customer success platform.

**Arguments**

* `user` (`UserDB`): the updated user.
* `update_dict` (`Dict[str, Any]`): dictionary with the updated user fields.
* `request` (`Optional[Request]`): optional FastAPI request object that triggered the operation. Defaults to None.

**Example**

```py
from fastapi_users import BaseUserManager


class UserManager(BaseUserManager[UserCreate, UserDB]):
    # ...
    async def on_after_update(
        self,
        user: UserDB,
        update_dict: Dict[str, Any],
        request: Optional[Request] = None,
    ):
        print(f"User {user.id} has been updated with {update_dict}.")
```

#### `on_after_request_verify`

Perform logic after successful verification request.

Typically, you'll want to **send an e-mail** with the link (and the token) that allows the user to verify their e-mail.

**Arguments**

* `user` (`UserDB`): the user to verify.
* `token` (`str`): the verification token.
* `request` (`Optional[Request]`): optional FastAPI request object that triggered the operation. Defaults to None.

**Example**

```py
from fastapi_users import BaseUserManager


class UserManager(BaseUserManager[UserCreate, UserDB]):
    # ...
    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
```

#### `on_after_verify`

Perform logic after successful user verification.

This may be useful if you wish to send another e-mail or store this information in a data analytics or customer success platform.

**Arguments**

* `user` (`UserDB`): the verified user.
* `request` (`Optional[Request]`): optional FastAPI request object that triggered the operation. Defaults to None.

**Example**

```py
from fastapi_users import BaseUserManager


class UserManager(BaseUserManager[UserCreate, UserDB]):
    # ...
    async def on_after_verify(
        self, user: UserDB, request: Optional[Request] = None
    ):
        print(f"User {user.id} has been verified")
```

#### `on_after_forgot_password`

Perform logic after successful forgot password request.

Typically, you'll want to **send an e-mail** with the link (and the token) that allows the user to reset their password.

**Arguments**

* `user` (`UserDB`): the user that forgot its password.
* `token` (`str`): the forgot password token
* `request` (`Optional[Request]`): optional FastAPI request object that triggered the operation. Defaults to None.

**Example**

```py
from fastapi_users import BaseUserManager


class UserManager(BaseUserManager[UserCreate, UserDB]):
    # ...
    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")
```

#### `on_after_reset_password`

Perform logic after successful password reset.

For example, you may want to **send an e-mail** to the concerned user to warn him that their password has been changed and that they should take action if they think they have been hacked.

**Arguments**

* `user` (`UserDB`): the user that reset its password.
* `request` (`Optional[Request]`): optional FastAPI request object that triggered the operation. Defaults to None.

**Example**

```py
from fastapi_users import BaseUserManager


class UserManager(BaseUserManager[UserCreate, UserDB]):
    # ...
    async def on_after_reset_password(self, user: UserDB, request: Optional[Request] = None):
        print(f"User {user.id} has reset their password.")
```
