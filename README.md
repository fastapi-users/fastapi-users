# FastAPI Users

<p align="center">
  <img src="https://raw.githubusercontent.com/frankie567/fastapi-users/master/logo.svg?sanitize=true" alt="FastAPI Users">
</p>

<p align="center">
    <em>Ready-to-use and customizable users management for FastAPI </em>
</p>

[![build](https://github.com/frankie567/fastapi-users/workflows/Build/badge.svg)](https://github.com/frankie567/fastapi-users/actions)
[![codecov](https://codecov.io/gh/frankie567/fastapi-users/branch/master/graph/badge.svg)](https://codecov.io/gh/frankie567/fastapi-users)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=frankie567/fastapi-users)](https://dependabot.com)
[![PyPI version](https://badge.fury.io/py/fastapi-users.svg)](https://badge.fury.io/py/fastapi-users)

---

**Documentation**: <a href="https://frankie567.github.io/fastapi-users/" target="_blank">https://frankie567.github.io/fastapi-users/</a>

**Source Code**: <a href="https://github.com/frankie567/fastapi-users" target="_blank">https://github.com/frankie567/fastapi-users</a>

---

Add quickly a registration and authentication system to your [FastAPI](https://fastapi.tiangolo.com/) project. **FastAPI Users** is designed to be as customizable and adaptable as possible.

## Features

* [X] Extensible base user model
* [X] Ready-to-use register, login, forgot and reset password routes.
* [X] Dependency callables to inject current user in route.
* [X] Customizable database backend
    * [X] SQLAlchemy async backend included thanks to [encode/databases](https://www.encode.io/databases/)
    * [X] MongoDB async backend included thanks to [mongodb/motor](https://github.com/mongodb/motor)
* [X] Customizable authentication backend
    * [X] JWT authentication backend included

## License

This project is licensed under the terms of the MIT license.
