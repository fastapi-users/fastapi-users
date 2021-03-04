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
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-24-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
<p align="center">
    <a href="https://www.buymeacoffee.com/frankie567" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/arial-red.png" alt="Buy Me A Coffee" height="40"></a>
</p>

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
    * [X] [ormar](https://collerek.github.io/ormar/) backend included

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
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/mark-todd"><img src="https://avatars.githubusercontent.com/u/60781787?v=4?s=100" width="100px;" alt=""/><br /><sub><b>mark-todd</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=mark-todd" title="Code">💻</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=mark-todd" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/lill74"><img src="https://avatars.githubusercontent.com/u/12353597?v=4?s=100" width="100px;" alt=""/><br /><sub><b>lill74</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/issues?q=author%3Alill74" title="Bug reports">🐛</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=lill74" title="Code">💻</a></td>
    <td align="center"><a href="https://yacht.sh"><img src="https://avatars.githubusercontent.com/u/66331933?v=4?s=100" width="100px;" alt=""/><br /><sub><b>SelfhostedPro</b></sub></a><br /><a href="#security-SelfhostedPro" title="Security">🛡️</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=SelfhostedPro" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/oskar-gmerek"><img src="https://avatars.githubusercontent.com/u/53402105?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Oskar Gmerek</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=oskar-gmerek" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/mcolladoio"><img src="https://avatars.githubusercontent.com/u/61695048?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Martin Collado</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/issues?q=author%3Amcolladoio" title="Bug reports">🐛</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=mcolladoio" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/nullhack"><img src="https://avatars.githubusercontent.com/u/11466701?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Eric Lopes</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=nullhack" title="Documentation">📖</a> <a href="#security-nullhack" title="Security">🛡️</a></td>
    <td align="center"><a href="https://github.com/rnd42"><img src="https://avatars.githubusercontent.com/u/618839?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Beau Breon</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=rnd42" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/niazangels"><img src="https://avatars.githubusercontent.com/u/2761491?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Niyas Mohammed</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=niazangels" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/prostomarkeloff"><img src="https://avatars.githubusercontent.com/u/28061158?v=4?s=100" width="100px;" alt=""/><br /><sub><b>prostomarkeloff</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=prostomarkeloff" title="Documentation">📖</a> <a href="https://github.com/frankie567/fastapi-users/commits?author=prostomarkeloff" title="Code">💻</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/mariusmezerette/"><img src="https://avatars.githubusercontent.com/u/952685?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Marius Mézerette</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/issues?q=author%3AMariusMez" title="Bug reports">🐛</a> <a href="#ideas-MariusMez" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/grigi"><img src="https://avatars.githubusercontent.com/u/1309160?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nickolas Grigoriadis</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/issues?q=author%3Agrigi" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://opendatacoder.me"><img src="https://avatars.githubusercontent.com/u/7386680?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Open Data Coder</b></sub></a><br /><a href="#ideas-p3t3r67x0" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://www.dralshehri.com/"><img src="https://avatars.githubusercontent.com/u/542855?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Mohammed Alshehri</b></sub></a><br /><a href="#ideas-dralshehri" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/lefnire/"><img src="https://avatars.githubusercontent.com/u/195202?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Tyler Renelle</b></sub></a><br /><a href="#ideas-lefnire" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/collerek"><img src="https://avatars.githubusercontent.com/u/16324238?v=4?s=100" width="100px;" alt=""/><br /><sub><b>collerek</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=collerek" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/rbracco"><img src="https://avatars.githubusercontent.com/u/47190785?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Robert Bracco</b></sub></a><br /><a href="#financial-rbracco" title="Financial">💵</a></td>
    <td align="center"><a href="https://herrmann.tech"><img src="https://avatars.githubusercontent.com/u/1058414?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Augusto Herrmann</b></sub></a><br /><a href="https://github.com/frankie567/fastapi-users/commits?author=augusto-herrmann" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Development

### Setup environment

You should create a virtual environment and activate it:

```bash
python -m venv venv/
```

```bash
source venv/bin/activate
```

And then install the development dependencies:

```bash
pip install -r requirements.dev.txt
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
