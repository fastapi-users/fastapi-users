# FastAPI Users

<p align="center">
  <img src="https://raw.githubusercontent.com/frankie567/fastapi-users/master/logo.svg?sanitize=true" alt="FastAPI Users">
</p>

<p align="center">
    <em>Ready-to-use and customizable users management for FastAPI </em>
</p>

[![build](https://github.com/frankie567/fastapi-users/workflows/Build/badge.svg)](https://github.com/frankie567/fastapi-users/actions)
[![codecov](https://codecov.io/gh/frankie567/fastapi-users/branch/master/graph/badge.svg)](https://codecov.io/gh/frankie567/fastapi-users)
[![PyPI version](https://badge.fury.io/py/fastapi-users.svg)](https://badge.fury.io/py/fastapi-users)
[![Downloads](https://pepy.tech/badge/fastapi-users)](https://pepy.tech/project/fastapi-users)

---

**Documentation**: <a href="https://frankie567.github.io/fastapi-users/" target="_blank">https://frankie567.github.io/fastapi-users/</a>

**Source Code**: <a href="https://github.com/frankie567/fastapi-users" target="_blank">https://github.com/frankie567/fastapi-users</a>

---

Add quickly a registration and authentication system to your [FastAPI](https://fastapi.tiangolo.com/) project. **FastAPI Users** is designed to be as customizable and adaptable as possible.

## Features

* [X] Extensible base user model
* [X] Ready-to-use register, login, forgot and reset password routes
* [X] Ready-to-use OAuth2 flow
* [X] Dependency callables to inject current user in route
* [X] Customizable database backend
    * [X] SQLAlchemy async backend included thanks to [encode/databases](https://www.encode.io/databases/)
    * [X] MongoDB async backend included thanks to [mongodb/motor](https://github.com/mongodb/motor)
    * [X] [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/) backend included
* [X] Multiple customizable authentication backends
    * [X] JWT authentication backend included
    * [X] Cookie authentication backend included
* [X] Full OpenAPI schema support, even with several authentication backends

## Development

### Setup environement

You should have [Pipenv](https://pipenv.readthedocs.io/en/latest/) installed. Then, you can install the dependencies with:

```bash
pipenv install --dev
```

After that, activate the virtual environment:

```bash
pipenv shell
```

### Run unit tests

You can run all the tests with:

```bash
make test
```

The command will start a MongoDB container for the related unit tests. So you should have [Docker](https://www.docker.com/get-started) installed.

Alternatively, you can run `pytest` yourself. The MongoDB unit tests will be skipped if no server is available on your local machine:

```bash
pytest
```

### Format the code

Execute the following command to apply `isort` and `black` formatting:

```bash
make format
```

## License

This project is licensed under the terms of the MIT license.
