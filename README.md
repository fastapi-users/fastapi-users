# FastAPI Users

<p align="center">
  <img src="https://raw.githubusercontent.com/fastapi-users/fastapi-users/master/logo.svg?sanitize=true" alt="FastAPI Users">
</p>

<p align="center">
    <em>Ready-to-use and customizable users management for FastAPI </em>
</p>

[![build](https://github.com/fastapi-users/fastapi-users/workflows/Build/badge.svg)](https://github.com/fastapi-users/fastapi-users/actions)
[![codecov](https://codecov.io/gh/fastapi-users/fastapi-users/branch/master/graph/badge.svg)](https://codecov.io/gh/fastapi-users/fastapi-users)
[![PyPI version](https://badge.fury.io/py/fastapi-users.svg)](https://badge.fury.io/py/fastapi-users)
[![Downloads](https://pepy.tech/badge/fastapi-users)](https://pepy.tech/project/fastapi-users)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-52-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
<p align="center">
<a href="https://www.buymeacoffee.com/frankie567"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=frankie567&button_colour=FF5F5F&font_colour=ffffff&font_family=Arial&outline_colour=000000&coffee_colour=FFDD00"></a>
</p>

---

**Documentation**: <a href="https://fastapi-users.github.io/fastapi-users/" target="_blank">https://fastapi-users.github.io/fastapi-users/</a>

**Source Code**: <a href="https://github.com/fastapi-users/fastapi-users" target="_blank">https://github.com/fastapi-users/fastapi-users</a>

---

Add quickly a registration and authentication system to your [FastAPI](https://fastapi.tiangolo.com/) project. **FastAPI Users** is designed to be as customizable and adaptable as possible.

## Features

* [X] Extensible base user model
* [X] Ready-to-use register, login, reset password and verify e-mail routes
* [X] Ready-to-use social OAuth2 login flow
* [X] Dependency callables to inject current user in route
* [X] Pluggable password validation
* [X] Customizable database backend
    * [X] [SQLAlchemy ORM async](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html) backend included
    * [X] MongoDB async backend included thanks to [mongodb/motor](https://github.com/mongodb/motor)
    * [X] [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/) backend included
    * [X] [ormar](https://collerek.github.io/ormar/) backend included
* [X] Multiple customizable authentication backends
    * [X] Transports: Authorization header, Cookie
    * [X] Strategies: JWT, Database, Redis
* [X] Full OpenAPI schema support, even with several authentication backends

## 📚 Discover my book: *Building Data Science Applications with FastAPI*

<img src="https://static.packt-cdn.com/products/9781801079211/cover/smaller" alt="Building Data Science Applications with FastAPI" height="256px" align="right">

**Develop, manage, and deploy efficient machine learning applications with Python**

### What is this book about?

This book covers the following exciting features:

* Explore the basics of modern Python and async I/O programming
* Get to grips with basic and advanced concepts of the FastAPI framework
* Implement a FastAPI dependency to efficiently run a machine learning model
* Integrate a simple face detection algorithm in a FastAPI backend
* Integrate common Python data science libraries in a web backend
* Deploy a performant and reliable web backend for a data science application

If you feel this book is for you, get your [copy](https://amzn.to/3kTvgjG) today!

## Contributors and sponsors ✨☕️

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://francoisvoron.com"><img src="https://avatars.githubusercontent.com/u/1144727?v=4?s=100" width="100px;" alt=""/><br /><sub><b>François Voron</b></sub></a><br /><a href="#maintenance-frankie567" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/paolodina"><img src="https://avatars.githubusercontent.com/u/1157401?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Paolo Dina</b></sub></a><br /><a href="#financial-paolodina" title="Financial">💵</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=paolodina" title="Code">💻</a></td>
    <td align="center"><a href="https://freelancehunt.com/freelancer/slado122.html"><img src="https://avatars.githubusercontent.com/u/46085159?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Dmytro Ohorodnik</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Aslado122" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://matthewscholefield.github.io"><img src="https://avatars.githubusercontent.com/u/5875019?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Matthew D. Scholefield</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AMatthewScholefield" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/roywes"><img src="https://avatars.githubusercontent.com/u/3861579?v=4?s=100" width="100px;" alt=""/><br /><sub><b>roywes</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Aroywes" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=roywes" title="Code">💻</a></td>
    <td align="center"><a href="https://devwriters.com"><img src="https://avatars.githubusercontent.com/u/10217535?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Satwik Kansal</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=satwikkansal" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/eddsalkield"><img src="https://avatars.githubusercontent.com/u/30939717?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Edd Salkield</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=eddsalkield" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=eddsalkield" title="Documentation">📖</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/mark-todd"><img src="https://avatars.githubusercontent.com/u/60781787?v=4?s=100" width="100px;" alt=""/><br /><sub><b>mark-todd</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=mark-todd" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=mark-todd" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/lill74"><img src="https://avatars.githubusercontent.com/u/12353597?v=4?s=100" width="100px;" alt=""/><br /><sub><b>lill74</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Alill74" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=lill74" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=lill74" title="Documentation">📖</a></td>
    <td align="center"><a href="https://yacht.sh"><img src="https://avatars.githubusercontent.com/u/66331933?v=4?s=100" width="100px;" alt=""/><br /><sub><b>SelfhostedPro</b></sub></a><br /><a href="#security-SelfhostedPro" title="Security">🛡️</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=SelfhostedPro" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/oskar-gmerek"><img src="https://avatars.githubusercontent.com/u/53402105?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Oskar Gmerek</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=oskar-gmerek" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/mcolladoio"><img src="https://avatars.githubusercontent.com/u/61695048?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Martin Collado</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Amcolladoio" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=mcolladoio" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/nullhack"><img src="https://avatars.githubusercontent.com/u/11466701?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Eric Lopes</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=nullhack" title="Documentation">📖</a> <a href="#security-nullhack" title="Security">🛡️</a></td>
    <td align="center"><a href="https://github.com/rnd42"><img src="https://avatars.githubusercontent.com/u/618839?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Beau Breon</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=rnd42" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/niazangels"><img src="https://avatars.githubusercontent.com/u/2761491?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Niyas Mohammed</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=niazangels" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/prostomarkeloff"><img src="https://avatars.githubusercontent.com/u/28061158?v=4?s=100" width="100px;" alt=""/><br /><sub><b>prostomarkeloff</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=prostomarkeloff" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=prostomarkeloff" title="Code">💻</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/mariusmezerette/"><img src="https://avatars.githubusercontent.com/u/952685?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Marius Mézerette</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AMariusMez" title="Bug reports">🐛</a> <a href="#ideas-MariusMez" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/grigi"><img src="https://avatars.githubusercontent.com/u/1309160?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nickolas Grigoriadis</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Agrigi" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://opendatacoder.me"><img src="https://avatars.githubusercontent.com/u/7386680?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Open Data Coder</b></sub></a><br /><a href="#ideas-p3t3r67x0" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://www.dralshehri.com/"><img src="https://avatars.githubusercontent.com/u/542855?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Mohammed Alshehri</b></sub></a><br /><a href="#ideas-dralshehri" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/lefnire/"><img src="https://avatars.githubusercontent.com/u/195202?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Tyler Renelle</b></sub></a><br /><a href="#ideas-lefnire" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/collerek"><img src="https://avatars.githubusercontent.com/u/16324238?v=4?s=100" width="100px;" alt=""/><br /><sub><b>collerek</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=collerek" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/rbracco"><img src="https://avatars.githubusercontent.com/u/47190785?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Robert Bracco</b></sub></a><br /><a href="#financial-rbracco" title="Financial">💵</a></td>
    <td align="center"><a href="https://herrmann.tech"><img src="https://avatars.githubusercontent.com/u/1058414?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Augusto Herrmann</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=augusto-herrmann" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/Smithybrewer"><img src="https://avatars.githubusercontent.com/u/57669591?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Smithybrewer</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3ASmithybrewer" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/silllli"><img src="https://avatars.githubusercontent.com/u/9334305?v=4?s=100" width="100px;" alt=""/><br /><sub><b>silllli</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=silllli" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/alexferrari88"><img src="https://avatars.githubusercontent.com/u/49028826?v=4?s=100" width="100px;" alt=""/><br /><sub><b>alexferrari88</b></sub></a><br /><a href="#financial-alexferrari88" title="Financial">💵</a></td>
    <td align="center"><a href="https://github.com/sandalwoodbox"><img src="https://avatars.githubusercontent.com/u/80227316?v=4?s=100" width="100px;" alt=""/><br /><sub><b>sandalwoodbox</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Asandalwoodbox" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/vladhoi"><img src="https://avatars.githubusercontent.com/u/33840957?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Vlad Hoi</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=vladhoi" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/jnu"><img src="https://avatars.githubusercontent.com/u/1069899?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Joe Nudell</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Ajnu" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/cosmosquark"><img src="https://avatars.githubusercontent.com/u/1540682?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Ben</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=cosmosquark" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/BoYanZh"><img src="https://avatars.githubusercontent.com/u/32470225?v=4?s=100" width="100px;" alt=""/><br /><sub><b>BoYanZh</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=BoYanZh" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/davidbrochart"><img src="https://avatars.githubusercontent.com/u/4711805?v=4?s=100" width="100px;" alt=""/><br /><sub><b>David Brochart</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=davidbrochart" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=davidbrochart" title="Code">💻</a></td>
    <td align="center"><a href="https://www.daanbeverdam.com"><img src="https://avatars.githubusercontent.com/u/13944585?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Daan Beverdam</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=daanbeverdam" title="Code">💻</a></td>
    <td align="center"><a href="http://sralab.com"><img src="https://avatars.githubusercontent.com/u/1815?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Stéphane Raimbault</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=stephane" title="Tests">⚠️</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Astephane" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/sondrelg"><img src="https://avatars.githubusercontent.com/u/25310870?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Sondre Lillebø Gundersen</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=sondrelg" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/maximka1221"><img src="https://avatars.githubusercontent.com/u/1503245?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Maxim</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=maximka1221" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Amaximka1221" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/scottdavort"><img src="https://avatars.githubusercontent.com/u/58272461?v=4?s=100" width="100px;" alt=""/><br /><sub><b>scottdavort</b></sub></a><br /><a href="#financial-scottdavort" title="Financial">💵</a></td>
    <td align="center"><a href="https://github.com/jdukewich"><img src="https://avatars.githubusercontent.com/u/37190801?v=4?s=100" width="100px;" alt=""/><br /><sub><b>John Dukewich</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=jdukewich" title="Documentation">📖</a></td>
    <td align="center"><a href="http://yezz.me"><img src="https://avatars.githubusercontent.com/u/52716203?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Yasser Tahiri</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=yezz123" title="Code">💻</a></td>
    <td align="center"><a href="https://www.brandongoding.tech"><img src="https://avatars.githubusercontent.com/u/17888319?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Brandon H. Goding</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=BrandonGoding" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/PovilasKud"><img src="https://avatars.githubusercontent.com/u/7852173?v=4?s=100" width="100px;" alt=""/><br /><sub><b>PovilasK</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=PovilasKud" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="http://justobjects.nl"><img src="https://avatars.githubusercontent.com/u/582630?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Just van den Broecke</b></sub></a><br /><a href="#financial-justb4" title="Financial">💵</a></td>
    <td align="center"><a href="https://github.com/jakemanger"><img src="https://avatars.githubusercontent.com/u/52495554?v=4?s=100" width="100px;" alt=""/><br /><sub><b>jakemanger</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Ajakemanger" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=jakemanger" title="Code">💻</a></td>
    <td align="center"><a href="https://bandism.net/"><img src="https://avatars.githubusercontent.com/u/22633385?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Ikko Ashimine</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=eltociear" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/matyasrichter"><img src="https://avatars.githubusercontent.com/u/20258539?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Matyáš Richter</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=matyasrichter" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Hazedd"><img src="https://avatars.githubusercontent.com/u/20663495?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Hazedd</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AHazedd" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=Hazedd" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/luisroel91"><img src="https://avatars.githubusercontent.com/u/44761184?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Luis Roel</b></sub></a><br /><a href="#financial-luisroel91" title="Financial">💵</a></td>
    <td align="center"><a href="https://ae-mc.ru"><img src="https://avatars.githubusercontent.com/u/43097289?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Alexandr Makurin</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=Ae-Mc" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AAe-Mc" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="http://www.retoflow.de"><img src="https://avatars.githubusercontent.com/u/23637821?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Leon Thurner</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=lthurner" title="Documentation">📖</a></td>
    <td align="center"><a href="http://meka.rs"><img src="https://avatars.githubusercontent.com/u/610855?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Goran Mekić</b></sub></a><br /><a href="#platform-mekanix" title="Packaging/porting to new platform">📦</a></td>
    <td align="center"><a href="https://gaganpreet.in/"><img src="https://avatars.githubusercontent.com/u/815873?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Gaganpreet</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=gaganpreet" title="Code">💻</a></td>
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

Alternatively, you can run `pytest` yourself.

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
