.. SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: WTFPL
.. No warranty.

Release Notes
=============

0.990.0
-------

- **Breaking**: Split the program into two Python packages (``core`` and
  ``app``). All plugins need to be updated accordingly.

- **Breaking**: Make entry points used by the package versioned for forward and
  backward compatibility.

- **Breaking**: Rename the implementation hook for plugins from ``hook_impl`` to
  ``cli_hook_impl``.

- **Breaking**: Split result types into a separate Python module.

- Add result reporters. Result reporter is a Python class, which is loadable via
  entry points and can output results of a certain type to the standard output.

- Add built-in result reporters for console and HTML.
  
- Add an option to list result reporters with ``find-work -R list``.

- Display exit messages to the standard error.

0.91.2
------

- Fix package name extraction algorithm. It is now based solely on regular
  expressions and might work more correctly than the previous approach.

- Include a Makefile to install manpages and shell completions in the sdist
  again.

- Add a little message in the ``--help`` output mentioning there's a man page.

0.91.1
------

- Fix options defined in custom commands.

- Improve start-up time by deferring loading of custom aliases.

- Improve start-up time by hardcoding system config file location to
  ``/etc/find-work/config.toml``.

- Process custom global flags in a more thoughtful way.

0.91.0
------

- **Breaking**: Plugins need to use ``find_work.plugins`` entry point group in
  order to register themselves. Turns out the former name was incorrect and
  broke many unrelated packages!

0.90.0
------

- **Breaking**: Modules are no longer shipped with find-work but installed as
  loadable plug-ins instead.

- **Breaking**: If you had custom aliases, you need to change ``command`` from
  a fully qualified import name to ``"plugin:command"`` syntax.

- **Gone**: ``pgo`` module, as Gentoo Packages website does no longer have
  GraphQL API.

- Implement Pydantic-based config parsing.

- Use striсter type validation here and here.

*Dependencies introduced:*

* :pypi:`pluggy`

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
