.. SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: WTFPL
.. No warranty.

Versioning and Backwards Compatibility
======================================

find-work follows the `SemVer 2.0.0 <https://semver.org/spec/v2.0.0.html>`_
version policy.

The following will result in a major version increment:

- Breaking :doc:`plugin API <reference>` changes.

- Breaking :doc:`configuration <configuration>` file format changes.

- Breaking command-line interface changes.

- Breaking machine-readable output format changes in any of result reporters.

Command-line plugins and result reporter plugins additionally have versioned
entry points. This prevents loading incompatible plugins in the first place.

Feature releases are made at irregular intervals when enough new features
accumulate. Bugfix releases may be made if bugs are discovered after a feature
release.

Plugin packages
---------------

Plugin packages developed in the `find-work-plugins`_ repo are also subject to
the Semantic Versioning policy.

.. _find-work-plugins: https://git.sysrq.in/find-work-plugins/tree/

The following will result in a major version increment:

- ``find_work.plugins.v{number}`` entry point version updates.

- Breaking :doc:`configuration <configuration>` file format changes.

- Breaking command-line interface changes.

Supported Python versions
-------------------------

Up to three most recent of stable-keyworded CPython versions in Gentoo are
supported.

Other versions and implementations might also work but they are not tested.
