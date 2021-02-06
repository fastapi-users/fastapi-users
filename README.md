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

<p align="center">
    <a href="https://www.buymeacoffee.com/frankie567" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/arial-red.png" alt="Buy Me A Coffee" height="40"></a>
</p>

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

---

**Documentation**: <a href="https://frankie567.github.io/fastapi-users/" target="_blank">https://frankie567.github.io/fastapi-users/</a>

**Source Code**: <a href="https://github.com/frankie567/fastapi-users" target="_blank">https://github.com/frankie567/fastapi-users</a>

---

Add quickly a registration and authentication system to your [FastAPI](https://fastapi.tiangolo.com/) project. **FastAPI Users** is designed to be as customizable and adaptable as possible.

## Features

* [X] Extensible base user model
* [X] Ready-to-use register, login, reset password and verify e-mail routes
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

## Contributors and sponsors ✨☕️

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://francoisvoron.com"><img src="https://avatars.githubusercontent.com/u/1144727?v=4?s=100" width="100px;" alt=""/><br /><sub><b>François Voron</b></sub></a><br /><a href="#maintenance-frankie567" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/paolodina"><img src="https://avatars.githubusercontent.com/u/1157401?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Paolo Dina</b></sub></a><br /><a href="#financial-paolodina" title="Financial">💵</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=paolodina" title="Code">💻</a></td>
    <td align="center"><a href="https://freelancehunt.com/freelancer/slado122.html"><img src="https://avatars.githubusercontent.com/u/46085159?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Dmytro Ohorodnik</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/issues?q=author%3Aslado122" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://matthewscholefield.github.io"><img src="https://avatars.githubusercontent.com/u/5875019?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Matthew D. Scholefield</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/issues?q=author%3AMatthewScholefield" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/roywes"><img src="https://avatars.githubusercontent.com/u/3861579?v=4?s=100" width="100px;" alt=""/><br /><sub><b>roywes</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/issues?q=author%3Aroywes" title="Bug reports">🐛</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=roywes" title="Code">💻</a></td>
    <td align="center"><a href="https://devwriters.com"><img src="https://avatars.githubusercontent.com/u/10217535?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Satwik Kansal</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=satwikkansal" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/eddsalkield"><img src="https://avatars.githubusercontent.com/u/30939717?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Edd Salkield</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=eddsalkield" title="Code">💻</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=eddsalkield" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/mark-todd"><img src="https://avatars.githubusercontent.com/u/60781787?v=4?s=100" width="100px;" alt=""/><br /><sub><b>mark-todd</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=mark-todd" title="Code">💻</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=mark-todd" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

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

There are quite a few unit tests, so you might run into ulimit issues where there are too many open file descriptors. You may be able to set a new, higher limit temporarily with:

```bash
ulimit -n 2048
```

### Format the code

Execute the following command to apply `isort` and `black` formatting:

```bash
make format
```

## License

This project is licensed under the terms of the MIT license.
