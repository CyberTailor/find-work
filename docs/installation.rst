.. SPDX-FileCopyrightText: 2022-2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: WTFPL
.. No warranty

Installation
============

.. tip::

   Most functionality is split into loadable plug-ins. Check them out!

   * :pypi:`find-work-bugzilla`
   * :pypi:`find-work-pkgcheck`
   * :pypi:`find-work-repology`

Prerequisites
-------------

You need either `pkgcore`_ or `Portage`_ at runtime to access package manager
functionality, such as filtering by installed packages.

.. _pkgcore: https://pkgcore.github.io/pkgcore/
.. _Portage: https://wiki.gentoo.org/wiki/Project:Portage

Gentoo
------

find-work and its plugins are packaged for Gentoo in the GURU ebuild repository.

.. prompt:: bash #

   eselect repository enable guru
   emaint sync -r guru
   emerge dev-util/find-work

Manual installation
-------------------

.. prompt:: bash

   pip install find-work --user

To install manual pages and shell completions, run:

.. prompt:: bash #

   make install-data

This way, plugins are not pulled automatically and you need to install them
manually as well.
