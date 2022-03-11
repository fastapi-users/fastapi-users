# JWT

[JSON Web Token (JWT)](https://jwt.io/introduction) is an internet standard for creating access tokens based on JSON. They don't need to be stored in a database: the data is self-contained inside and cryptographically signed.

## Configuration

```py
from fastapi_users.authentication import JWTStrategy

SECRET = "SECRET"

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)
```

As you can see, instantiation is quite simple. It accepts the following arguments:

- `secret` (`Union[str, pydantic.SecretStr]`): A constant secret which is used to encode the token. **Use a strong passphrase and keep it secure.**
- `lifetime_seconds` (`Optional[int]`): The lifetime of the token in seconds. Can be set to `None` but in this case the token will be valid **forever**; which may raise serious security concerns.
- `token_audience` (`Optional[List[str]]`): A list of valid audiences for the JWT token. Defaults to `["fastapi-users:auth"]`.
- `algorithm` (`Optional[str]`): The JWT encryption algorithm. See [RFC 7519, section 8](https://datatracker.ietf.org/doc/html/rfc7519#section-8). Defaults to `"HS256"`.
- `public_key` (`Optional[Union[str, pydantic.SecretStr]]`): If the JWT encryption algorithm requires a key pair instead of a simple secret, the key to **decrypt** the JWT may be provided here. The `secret` parameter will always be used to **encrypt** the JWT.

!!! tip "Why it's inside a function?"
    To allow strategies to be instantiated dynamically with other dependencies, they have to be provided as a callable to the authentication backend.

    For `JWTStrategy`, since it doesn't require dependencies, it can be as simple as the function above.

## RS256 example

```py
from fastapi_users.authentication import JWTStrategy

# IMPORTANT: provide your own public and private key!

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuTJw5+brGv8PX+ijZ994
ic5V1HgJSreUDnXzCYPiW7FTtwYRYA60nNFoQpnZaQMiQuQcA9Kl1Jx6+KB14Wcr
ApydV4ppLW0FCH5pFJVsyXOKTLCLuUNU3IRV2izpLQEgUSYWX7W1MEi5xBh82W//
uMiajTQrBBu0K0SV14aGSOUjeaqtB4N0gnrRHY9iKNF1M4QlPJ3EA/0i+9lkeB3N
zBv6EbOAtVkBfH2SMnrdGAzpBlVnWsDC7Bji59kXmGt7xb40xqDuWXJJGRM4UpEk
P5cvg2vUJYeqg9cTRBfWPJCgQL9864rOmUOCJV9meRY4wB2IP2qrxWVyijDDfxOQ
bQIDAQAB
-----END PUBLIC KEY-----"""

PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAuTJw5+brGv8PX+ijZ994ic5V1HgJSreUDnXzCYPiW7FTtwYR
YA60nNFoQpnZaQMiQuQcA9Kl1Jx6+KB14WcrApydV4ppLW0FCH5pFJVsyXOKTLCL
uUNU3IRV2izpLQEgUSYWX7W1MEi5xBh82W//uMiajTQrBBu0K0SV14aGSOUjeaqt
B4N0gnrRHY9iKNF1M4QlPJ3EA/0i+9lkeB3NzBv6EbOAtVkBfH2SMnrdGAzpBlVn
WsDC7Bji59kXmGt7xb40xqDuWXJJGRM4UpEkP5cvg2vUJYeqg9cTRBfWPJCgQL98
64rOmUOCJV9meRY4wB2IP2qrxWVyijDDfxOQbQIDAQABAoIBABK0dsVhZBkZrlia
Q1jUMBVBFxeq2QtoH8bXIGkzXhszPZiUfxBD4/ebyetCJTyPQbheWDsFnVSsSlpO
wKE3vZcZsOWc1/Mr2fCJ7fyTfAWbyxnkUfRwCcPtBMvQsetm+/feQC/CB08dZU/a
Rk/i2UH1VvDQllCnqKqfFoBKeMknWRw8WbsErQkPfpQqhKdV3JFSIaowECPWf/Ar
P68eJQf+sOBmBejTys/c8mPP9xgRZjCvkauBB6eIM8nh3fftQazZwfeLxgeCv9hM
BeJoUAFF0dM5d26G1fL8gHzPfWiVPAjkuYZ61NJNeor/SfOtQAC3tMZeEAfqRuoB
i2vzQWECgYEAvGqO/fUJkIT1EzmoUQbRSJe9zBMi0s8/n+b7zheoUToiZnpkjmUZ
Pwpk+NSYQVmRln1+XsdAAB4CiCZbXjgAQyJ5yBM/ZFgioaXv8lTizIP0qD9KdTPp
3occZd4Dc+0FRHK5bnqntwGm32vBDMDDnYMU7y4fXnVUVvUIqPZQnaECgYEA+6BG
zFg4eDkF23N9X/pFaAkNngonf2sI4Qu2MV9QohbdEXwQ0BKN9IYeqUp04ZIVP7c/
7Qbrx0d+chy/pFN2sbI/LnhuTwFFeANS1jQM8gEo/PjWiclQ+D+A7UIwpaQmdeBi
YIBmvXlgLFJ/euUXSBQd7+tUyAUcvvHkM+LMx00CgYEAhsIL3XUZTyTZB9QQH0up
+aqV09TH7lDOZ7ZT2JYxC09x9SuKqhGC2gS8LQAYmXzPVPwSmwUVMEBGfUw5wwx4
m4uX4FJr33/t3QGKuR6fS7kBDiieP29O0Jp/5BfDDnGyd786Att1Ar4KtPcjjtR7
1DdBjMPHKc7u8Ha2p+nrxKECgYBCLjyQwF9R14Wf23dNSBD7NO5c88TBsZArSJ5J
zAz0JNlOIPh3EXo+pwvncMrfDUIDeRoaKGjZCAfM0ZziBoXAZOZTPZ+drfLshstB
xXzmJcH3Dye2I7nlISaywGb1GgB3nmWhhgP/r63I2oXm99wwvAHHuXiaByYxXoOr
1eoQPQKBgGYik9wKi53DCVJnr2bDN3egeopd42fgugZj6dRhR4oah3UGDJhgHvRP
HlxTyCk/Faz12QDxC3xD7McaeWJhWRqHB2wmf84thDVS3cAx2QBS/rYIFlQMH3n4
61Jy6v3cMwId7vHHgzNoJIJCSROyTQ9UVfvNLPx9pWXsD0wxeX9w
-----END RSA PRIVATE KEY-----"""

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=PRIVATE_KEY, 
        lifetime_seconds=3600,
        algorithm="RS256",
        public_key=PUBLIC_KEY,
    )
```

## Logout

On logout, this strategy **won't do anything**. Indeed, a JWT can't be invalidated on the server-side: it's valid until it expires.
