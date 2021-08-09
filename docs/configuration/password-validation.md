# Password validation

FastAPI Users **doesn't have any password validation logic by default**. However, there is an argument on the `FastAPIUsers` class so that you can provide your own password validation function.

It'll be applied on each routes that need to validate the input password:

* At registration ([`/register`](../usage/routes.md#post-register))
* At password reset ([`/reset-password`](../usage/routes.md#post-reset-password))
* At profile update ([`/me`](../usage/routes.md#patch-me) and [`/{user_id}`](../usage/routes.md#patch-user_id))

## Configuration

The FastAPIUsers class accepts an optional keyword argument `validate_password`. It expects an async function which accepts in argument:

* `password` (`str`): the password to validate.
* `user` (`Union[UserRegister, User]`): user model which we are currently validating the password. Useful if you want to check that the password doesn't contain the name or the birthdate of the user for example.

This function should return `None` if the password is valid or raise `InvalidPasswordException` if not. This exception expects an argument `reason` telling why the password is invalid. It'll be part of the error response.

## Example

```py
from fastapi_users import FastAPIUsers, InvalidPasswordException


async def validate_password(
    password: str,
    user: Union[UserCreate, User],
) -> None:
    if len(password) < 8:
        raise InvalidPasswordException(
            reason="Password should be at least 8 characters"
        )
    if user.email in password:
        raise InvalidPasswordException(
            reason="Password should not contain e-mail"
        )


fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
    validate_password=validate_password
)
```
