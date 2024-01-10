.. SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: WTFPL
.. No warranty.

Release Notes
=============

0.3.0
-----

* **New:** Discover version bump requests on Bugzilla (command: ``bugzilla
  outdated``).

* **New:** Discover outdated packages in the Gentoo repository (command: ``pgo
  outdated``).

* **New:** Discover stabilization candidates in the Gentoo repository (command:
  ``pgo stabilization``).

* **New:** Filter results by maintainer.

* Dependencies introduced:

  * :pypi:`python-bugzilla`
  * :pypi:`requests`
  * :pypi:`tabulate`
  * :pypi:`pytest-recording` *(test)*

0.2.0
-----

* Add progress indication with the option to disable it.
* Support ``NO_COLOR`` variable in addition to ``NOCOLOR``.
* [repology/outdated]: fix :bug:`2`, where different packages of the same
  projects crashed the utility.
* [repology/outdated]: use ``origversion`` if defined to prevent crashes.

0.1.1
-----

* [repology/outdated]: print latest of packaged version instead of a random one.

0.1.0
-----

* First release.
