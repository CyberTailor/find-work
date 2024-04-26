.. SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: WTFPL
.. No warranty.

Release Notes
=============

0.7.0
-----

- **New**: Filter oudated packages by version part (:bug:`4`).

- Use Pydantic models to load and serialize caches. This could have better
  perfomance and correctness but also introduce new bugs.

*Modules changelog:*

- **bugzilla**:

  - Switch to REST API from XMLRPC.

- **pgo**:

  - **outdated**:

    - Improve error text for trying to filter by maintainer (:bug:`3`).

0.6.1
-----

*Modules changelog:*

- **pkgcheck**:

  - **scan**:

    - Drop ``--quiet`` flag. Before pkgcheck v0.10.21, this option was used
      only in pkgcore internals. Now it's used to filter out non-error results
      from pkgcheck.

0.6.0
-----

- **New:** Define custom global flags to override global options.

*Modules changelog:*

- **pkgcheck**:

  - **New:** Filter results by keyword or message.

  - Silence pkgcore warnings and pkgcheck status messages.

0.5.0
-----

- **New:** Scan repository for QA issues (command: ``pkgcheck scan``).

- Fix caching with maintainer filter applied.

*Dependencies introduced:*

* :pypi:`pkgcheck`

0.4.0
-----

- **New:** Execute custom aliases.

- **New:** List all bugs on Bugzilla (command: ``bugzilla list``).

- **Gone:** ``bugzilla outdated`` is now ``execute bump-requests``.

- **Gone:** Python 3.10 support.

- Fix parsing atoms that contain revision.

*Dependencies introduced:*

* :pypi:`deepmerge`
* :pypi:`platformdirs`

0.3.0
-----

- **New:** Discover version bump requests on Bugzilla (command: ``bugzilla
  outdated``).

- **New:** Discover outdated packages in the Gentoo repository (command: ``pgo
  outdated``).

- **New:** Discover stabilization candidates in the Gentoo repository (command:
  ``pgo stabilization``).

- **New:** Filter results by maintainer.

*Dependencies introduced:*

* :pypi:`python-bugzilla`
* :pypi:`requests`
* :pypi:`tabulate`
* :pypi:`pytest-recording` *(test)*

0.2.0
-----

- Add progress indication with the option to disable it.

- Support ``NO_COLOR`` variable in addition to ``NOCOLOR``.

*Modules changelog:*

- **repology**:

  - **outdated**:

    - Fix :bug:`2`, where different packages of the same project crashed the
      utility.

    - Use ``origversion`` if defined to prevent crashes.

0.1.1
-----

*Modules changelog:*

- **repology**:

  - **outdated**:

    - Output the latest of packaged versions instead of a choosing a random one.

0.1.0
-----

- First release.
