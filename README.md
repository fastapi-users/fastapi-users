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
[![All Contributors](https://img.shields.io/badge/all_contributors-77-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<p align="center">
<a href="https://github.com/sponsors/frankie567"><img src="https://md-buttons.francoisvoron.com/button.svg?text=Buy%20me%20a%20coffee%20%E2%98%95%EF%B8%8F&bg=ef4444&w=200&h=50"></a>
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
    * [X] [SQLAlchemy ORM async](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html) included
    * [X] [MongoDB with Beanie ODM](https://github.com/roman-right/beanie/) included
* [X] Multiple customizable authentication backends
    * [X] Transports: Authorization header, Cookie
    * [X] Strategies: JWT, Database, Redis
* [X] Full OpenAPI schema support, even with several authentication backends

## In a hurry? Discover Fief, the open-source authentication platform

<p align="center">
  <img src="https://raw.githubusercontent.com/fief-dev/.github/main/logos/logo-full-red.svg?sanitize=true" alt="Fief" width="256" style="width: 256px">
</p>

<img src="https://www.fief.dev/illustrations/guard-right.svg" alt="Fief" height="300" align="right" style="height: 300px">

**Implementing registration, login, social auth is hard and painful. We know it. With our highly secure and open-source users management platform, you can focus on your app while staying in control of your users data.**

* Based on **FastAPI Users**!
* **Open-source**: self-host it for free or use our hosted version
* **Bring your own database**: host your database anywhere, we'll take care of the rest
* **Pre-built login and registration pages**: clean and fast authentication so you don't have to do it yourself
* **Official Python client** with built-in **FastAPI integration**

<br clear="right"/>

<p align="center">
    <a href="https://www.fief.dev"><img src="https://md-buttons.francoisvoron.com/button.svg?text=Join%20the%20beta&bg=f43f5e&w=150&px=30" /></a>
</p>
<p align="center">It's free!</p>

## Contributors and sponsors ✨☕️

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://francoisvoron.com"><img src="https://avatars.githubusercontent.com/u/1144727?v=4?s=100" width="100px;" alt="François Voron"/><br /><sub><b>François Voron</b></sub></a><br /><a href="#maintenance-frankie567" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/paolodina"><img src="https://avatars.githubusercontent.com/u/1157401?v=4?s=100" width="100px;" alt="Paolo Dina"/><br /><sub><b>Paolo Dina</b></sub></a><br /><a href="#financial-paolodina" title="Financial">💵</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=paolodina" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://freelancehunt.com/freelancer/slado122.html"><img src="https://avatars.githubusercontent.com/u/46085159?v=4?s=100" width="100px;" alt="Dmytro Ohorodnik"/><br /><sub><b>Dmytro Ohorodnik</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Aslado122" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://matthewscholefield.github.io"><img src="https://avatars.githubusercontent.com/u/5875019?v=4?s=100" width="100px;" alt="Matthew D. Scholefield"/><br /><sub><b>Matthew D. Scholefield</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AMatthewScholefield" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/roywes"><img src="https://avatars.githubusercontent.com/u/3861579?v=4?s=100" width="100px;" alt="roywes"/><br /><sub><b>roywes</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Aroywes" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=roywes" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://devwriters.com"><img src="https://avatars.githubusercontent.com/u/10217535?v=4?s=100" width="100px;" alt="Satwik Kansal"/><br /><sub><b>Satwik Kansal</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=satwikkansal" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/eddsalkield"><img src="https://avatars.githubusercontent.com/u/30939717?v=4?s=100" width="100px;" alt="Edd Salkield"/><br /><sub><b>Edd Salkield</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=eddsalkield" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=eddsalkield" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mark-todd"><img src="https://avatars.githubusercontent.com/u/60781787?v=4?s=100" width="100px;" alt="mark-todd"/><br /><sub><b>mark-todd</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=mark-todd" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=mark-todd" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/lill74"><img src="https://avatars.githubusercontent.com/u/12353597?v=4?s=100" width="100px;" alt="lill74"/><br /><sub><b>lill74</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Alill74" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=lill74" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=lill74" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://yacht.sh"><img src="https://avatars.githubusercontent.com/u/66331933?v=4?s=100" width="100px;" alt="SelfhostedPro"/><br /><sub><b>SelfhostedPro</b></sub></a><br /><a href="#security-SelfhostedPro" title="Security">🛡️</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=SelfhostedPro" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/oskar-gmerek"><img src="https://avatars.githubusercontent.com/u/53402105?v=4?s=100" width="100px;" alt="Oskar Gmerek"/><br /><sub><b>Oskar Gmerek</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=oskar-gmerek" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mcolladoio"><img src="https://avatars.githubusercontent.com/u/61695048?v=4?s=100" width="100px;" alt="Martin Collado"/><br /><sub><b>Martin Collado</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Amcolladoio" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=mcolladoio" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/nullhack"><img src="https://avatars.githubusercontent.com/u/11466701?v=4?s=100" width="100px;" alt="Eric Lopes"/><br /><sub><b>Eric Lopes</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=nullhack" title="Documentation">📖</a> <a href="#security-nullhack" title="Security">🛡️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/rnd42"><img src="https://avatars.githubusercontent.com/u/618839?v=4?s=100" width="100px;" alt="Beau Breon"/><br /><sub><b>Beau Breon</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=rnd42" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/niazangels"><img src="https://avatars.githubusercontent.com/u/2761491?v=4?s=100" width="100px;" alt="Niyas Mohammed"/><br /><sub><b>Niyas Mohammed</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=niazangels" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/prostomarkeloff"><img src="https://avatars.githubusercontent.com/u/28061158?v=4?s=100" width="100px;" alt="prostomarkeloff"/><br /><sub><b>prostomarkeloff</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=prostomarkeloff" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=prostomarkeloff" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.linkedin.com/in/mariusmezerette/"><img src="https://avatars.githubusercontent.com/u/952685?v=4?s=100" width="100px;" alt="Marius Mézerette"/><br /><sub><b>Marius Mézerette</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AMariusMez" title="Bug reports">🐛</a> <a href="#ideas-MariusMez" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/grigi"><img src="https://avatars.githubusercontent.com/u/1309160?v=4?s=100" width="100px;" alt="Nickolas Grigoriadis"/><br /><sub><b>Nickolas Grigoriadis</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Agrigi" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://opendatacoder.me"><img src="https://avatars.githubusercontent.com/u/7386680?v=4?s=100" width="100px;" alt="Open Data Coder"/><br /><sub><b>Open Data Coder</b></sub></a><br /><a href="#ideas-p3t3r67x0" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.dralshehri.com/"><img src="https://avatars.githubusercontent.com/u/542855?v=4?s=100" width="100px;" alt="Mohammed Alshehri"/><br /><sub><b>Mohammed Alshehri</b></sub></a><br /><a href="#ideas-dralshehri" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.linkedin.com/in/lefnire/"><img src="https://avatars.githubusercontent.com/u/195202?v=4?s=100" width="100px;" alt="Tyler Renelle"/><br /><sub><b>Tyler Renelle</b></sub></a><br /><a href="#ideas-lefnire" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/collerek"><img src="https://avatars.githubusercontent.com/u/16324238?v=4?s=100" width="100px;" alt="collerek"/><br /><sub><b>collerek</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=collerek" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/rbracco"><img src="https://avatars.githubusercontent.com/u/47190785?v=4?s=100" width="100px;" alt="Robert Bracco"/><br /><sub><b>Robert Bracco</b></sub></a><br /><a href="#financial-rbracco" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://herrmann.tech"><img src="https://avatars.githubusercontent.com/u/1058414?v=4?s=100" width="100px;" alt="Augusto Herrmann"/><br /><sub><b>Augusto Herrmann</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=augusto-herrmann" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Smithybrewer"><img src="https://avatars.githubusercontent.com/u/57669591?v=4?s=100" width="100px;" alt="Smithybrewer"/><br /><sub><b>Smithybrewer</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3ASmithybrewer" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/silllli"><img src="https://avatars.githubusercontent.com/u/9334305?v=4?s=100" width="100px;" alt="silllli"/><br /><sub><b>silllli</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=silllli" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/alexferrari88"><img src="https://avatars.githubusercontent.com/u/49028826?v=4?s=100" width="100px;" alt="alexferrari88"/><br /><sub><b>alexferrari88</b></sub></a><br /><a href="#financial-alexferrari88" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sandalwoodbox"><img src="https://avatars.githubusercontent.com/u/80227316?v=4?s=100" width="100px;" alt="sandalwoodbox"/><br /><sub><b>sandalwoodbox</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Asandalwoodbox" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=sandalwoodbox" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/vladhoi"><img src="https://avatars.githubusercontent.com/u/33840957?v=4?s=100" width="100px;" alt="Vlad Hoi"/><br /><sub><b>Vlad Hoi</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=vladhoi" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jnu"><img src="https://avatars.githubusercontent.com/u/1069899?v=4?s=100" width="100px;" alt="Joe Nudell"/><br /><sub><b>Joe Nudell</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Ajnu" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/cosmosquark"><img src="https://avatars.githubusercontent.com/u/1540682?v=4?s=100" width="100px;" alt="Ben"/><br /><sub><b>Ben</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=cosmosquark" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/BoYanZh"><img src="https://avatars.githubusercontent.com/u/32470225?v=4?s=100" width="100px;" alt="BoYanZh"/><br /><sub><b>BoYanZh</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=BoYanZh" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/davidbrochart"><img src="https://avatars.githubusercontent.com/u/4711805?v=4?s=100" width="100px;" alt="David Brochart"/><br /><sub><b>David Brochart</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=davidbrochart" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=davidbrochart" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.daanbeverdam.com"><img src="https://avatars.githubusercontent.com/u/13944585?v=4?s=100" width="100px;" alt="Daan Beverdam"/><br /><sub><b>Daan Beverdam</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=daanbeverdam" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://sralab.com"><img src="https://avatars.githubusercontent.com/u/1815?v=4?s=100" width="100px;" alt="Stéphane Raimbault"/><br /><sub><b>Stéphane Raimbault</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=stephane" title="Tests">⚠️</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Astephane" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sondrelg"><img src="https://avatars.githubusercontent.com/u/25310870?v=4?s=100" width="100px;" alt="Sondre Lillebø Gundersen"/><br /><sub><b>Sondre Lillebø Gundersen</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=sondrelg" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/maximka1221"><img src="https://avatars.githubusercontent.com/u/1503245?v=4?s=100" width="100px;" alt="Maxim"/><br /><sub><b>Maxim</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=maximka1221" title="Documentation">📖</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Amaximka1221" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/scottdavort"><img src="https://avatars.githubusercontent.com/u/58272461?v=4?s=100" width="100px;" alt="scottdavort"/><br /><sub><b>scottdavort</b></sub></a><br /><a href="#financial-scottdavort" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jdukewich"><img src="https://avatars.githubusercontent.com/u/37190801?v=4?s=100" width="100px;" alt="John Dukewich"/><br /><sub><b>John Dukewich</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=jdukewich" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://yezz.me"><img src="https://avatars.githubusercontent.com/u/52716203?v=4?s=100" width="100px;" alt="Yasser Tahiri"/><br /><sub><b>Yasser Tahiri</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=yezz123" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.brandongoding.tech"><img src="https://avatars.githubusercontent.com/u/17888319?v=4?s=100" width="100px;" alt="Brandon H. Goding"/><br /><sub><b>Brandon H. Goding</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=BrandonGoding" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/PovilasKud"><img src="https://avatars.githubusercontent.com/u/7852173?v=4?s=100" width="100px;" alt="PovilasK"/><br /><sub><b>PovilasK</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=PovilasKud" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://justobjects.nl"><img src="https://avatars.githubusercontent.com/u/582630?v=4?s=100" width="100px;" alt="Just van den Broecke"/><br /><sub><b>Just van den Broecke</b></sub></a><br /><a href="#financial-justb4" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jakemanger"><img src="https://avatars.githubusercontent.com/u/52495554?v=4?s=100" width="100px;" alt="jakemanger"/><br /><sub><b>jakemanger</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Ajakemanger" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=jakemanger" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://bandism.net/"><img src="https://avatars.githubusercontent.com/u/22633385?v=4?s=100" width="100px;" alt="Ikko Ashimine"/><br /><sub><b>Ikko Ashimine</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=eltociear" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/matyasrichter"><img src="https://avatars.githubusercontent.com/u/20258539?v=4?s=100" width="100px;" alt="Matyáš Richter"/><br /><sub><b>Matyáš Richter</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=matyasrichter" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Hazedd"><img src="https://avatars.githubusercontent.com/u/20663495?v=4?s=100" width="100px;" alt="Hazedd"/><br /><sub><b>Hazedd</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AHazedd" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=Hazedd" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/luisroel91"><img src="https://avatars.githubusercontent.com/u/44761184?v=4?s=100" width="100px;" alt="Luis Roel"/><br /><sub><b>Luis Roel</b></sub></a><br /><a href="#financial-luisroel91" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://ae-mc.ru"><img src="https://avatars.githubusercontent.com/u/43097289?v=4?s=100" width="100px;" alt="Alexandr Makurin"/><br /><sub><b>Alexandr Makurin</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=Ae-Mc" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AAe-Mc" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://www.retoflow.de"><img src="https://avatars.githubusercontent.com/u/23637821?v=4?s=100" width="100px;" alt="Leon Thurner"/><br /><sub><b>Leon Thurner</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=lthurner" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://meka.rs"><img src="https://avatars.githubusercontent.com/u/610855?v=4?s=100" width="100px;" alt="Goran Mekić"/><br /><sub><b>Goran Mekić</b></sub></a><br /><a href="#platform-mekanix" title="Packaging/porting to new platform">📦</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://gaganpreet.in/"><img src="https://avatars.githubusercontent.com/u/815873?v=4?s=100" width="100px;" alt="Gaganpreet"/><br /><sub><b>Gaganpreet</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=gaganpreet" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jtv8"><img src="https://avatars.githubusercontent.com/u/29302451?v=4?s=100" width="100px;" alt="Joe Taylor"/><br /><sub><b>Joe Taylor</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=jtv8" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ricfri"><img src="https://avatars.githubusercontent.com/u/21967765?v=4?s=100" width="100px;" alt="Richard Friberg"/><br /><sub><b>Richard Friberg</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Aricfri" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.kentonparton.com"><img src="https://avatars.githubusercontent.com/u/20202312?v=4?s=100" width="100px;" alt="Kenton Parton"/><br /><sub><b>Kenton Parton</b></sub></a><br /><a href="#financial-KentonParton" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Qwizi"><img src="https://avatars.githubusercontent.com/u/23024321?v=4?s=100" width="100px;" alt="Adrian Ciołek"/><br /><sub><b>Adrian Ciołek</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3AQwizi" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://blog.obscuritylabs.com"><img src="https://avatars.githubusercontent.com/u/8761706?v=4?s=100" width="100px;" alt="⭕Alexander Rymdeko-Harvey"/><br /><sub><b>⭕Alexander Rymdeko-Harvey</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=killswitch-GUI" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://schwannden.com"><img src="https://avatars.githubusercontent.com/u/5753086?v=4?s=100" width="100px;" alt="schwannden"/><br /><sub><b>schwannden</b></sub></a><br /><a href="#maintenance-schwannden" title="Maintenance">🚧</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=schwannden" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://jimscope.is-a.dev"><img src="https://avatars.githubusercontent.com/u/27647007?v=4?s=100" width="100px;" alt="Jimmy Angel Pérez Díaz"/><br /><sub><b>Jimmy Angel Pérez Díaz</b></sub></a><br /><a href="#security-JimScope" title="Security">🛡️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://austinmartinorr.com"><img src="https://avatars.githubusercontent.com/u/8422403?v=4?s=100" width="100px;" alt="Austin Orr"/><br /><sub><b>Austin Orr</b></sub></a><br /><a href="#maintenance-austinorr" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://carlo.io"><img src="https://avatars.githubusercontent.com/u/299107?v=4?s=100" width="100px;" alt="Carlo Eugster"/><br /><sub><b>Carlo Eugster</b></sub></a><br /><a href="#security-carloe" title="Security">🛡️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.vzamboni.io"><img src="https://avatars.githubusercontent.com/u/1734279?v=4?s=100" width="100px;" alt="Vittorio Zamboni"/><br /><sub><b>Vittorio Zamboni</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=vittoriozamboni" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/aryadovoy"><img src="https://avatars.githubusercontent.com/u/26593349?v=4?s=100" width="100px;" alt="Andrey"/><br /><sub><b>Andrey</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=aryadovoy" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://linkedin.com/in/canhtartanoglu"><img src="https://avatars.githubusercontent.com/u/29519599?v=4?s=100" width="100px;" alt="Can H. Tartanoglu"/><br /><sub><b>Can H. Tartanoglu</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Acaniko" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/flipee"><img src="https://avatars.githubusercontent.com/u/22459623?v=4?s=100" width="100px;" alt="Filipe Nascimento"/><br /><sub><b>Filipe Nascimento</b></sub></a><br /><a href="#security-flipee" title="Security">🛡️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://duduru.website/"><img src="https://avatars.githubusercontent.com/u/50397689?v=4?s=100" width="100px;" alt="dudulu"/><br /><sub><b>dudulu</b></sub></a><br /><a href="#financial-hgalytoby" title="Financial">💵</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Ahgalytoby" title="Bug reports">🐛</a> <a href="#question-hgalytoby" title="Answering Questions">💬</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/antont"><img src="https://avatars.githubusercontent.com/u/201016?v=4?s=100" width="100px;" alt="Toni Alatalo"/><br /><sub><b>Toni Alatalo</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=antont" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=antont" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://bkis.github.io"><img src="https://avatars.githubusercontent.com/u/9215743?v=4?s=100" width="100px;" alt="Börge Kiss"/><br /><sub><b>Börge Kiss</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=bkis" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.praciano.com.br"><img src="https://avatars.githubusercontent.com/u/4080737?v=4?s=100" width="100px;" alt="Guilherme Caminha"/><br /><sub><b>Guilherme Caminha</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=gpkc" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sorasful"><img src="https://avatars.githubusercontent.com/u/32820423?v=4?s=100" width="100px;" alt="Téva KRIEF"/><br /><sub><b>Téva KRIEF</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=sorasful" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/EssaAlshammri"><img src="https://avatars.githubusercontent.com/u/10750698?v=4?s=100" width="100px;" alt="Essa Alshammri"/><br /><sub><b>Essa Alshammri</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=EssaAlshammri" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jankadel"><img src="https://avatars.githubusercontent.com/u/34775247?v=4?s=100" width="100px;" alt="0xJan"/><br /><sub><b>0xJan</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Ajankadel" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.justhomas.in/"><img src="https://avatars.githubusercontent.com/u/29140428?v=4?s=100" width="100px;" alt="Justin Thomas"/><br /><sub><b>Justin Thomas</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=justhomas" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.adamisrael.com/"><img src="https://avatars.githubusercontent.com/u/125008?v=4?s=100" width="100px;" alt="Adam Israel"/><br /><sub><b>Adam Israel</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=AdamIsrael" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Nerixjk"><img src="https://avatars.githubusercontent.com/u/32194858?v=4?s=100" width="100px;" alt="Nerixjk"/><br /><sub><b>Nerixjk</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3ANerixjk" title="Bug reports">🐛</a> <a href="https://github.com/fastapi-users/fastapi-users/commits?author=Nerixjk" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/fotinakis"><img src="https://avatars.githubusercontent.com/u/75300?v=4?s=100" width="100px;" alt="Mike Fotinakis"/><br /><sub><b>Mike Fotinakis</b></sub></a><br /><a href="https://github.com/fastapi-users/fastapi-users/commits?author=fotinakis" title="Code">💻</a> <a href="https://github.com/fastapi-users/fastapi-users/issues?q=author%3Afotinakis" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/lifengmds"><img src="https://avatars.githubusercontent.com/u/8794442?v=4?s=100" width="100px;" alt="lifengmds"/><br /><sub><b>lifengmds</b></sub></a><br /><a href="#financial-lifengmds" title="Financial">💵</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Development

### Setup environment

We use [Hatch](https://hatch.pypa.io/latest/install/) to manage the development environment and production build. Ensure it's installed on your system.

### Run unit tests

You can run all the tests with:

```bash
hatch run test:test
```

### Format the code

Execute the following command to apply linting and check typing:

```bash
hatch run lint
```

### Serve the documentation

You can serve the documentation locally with the following command:

```bash
hatch run docs
```

The documentation will be available on [http://localhost:8000](http://localhost:8000).

## License

This project is licensed under the terms of the MIT license.
