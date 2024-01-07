.. SPDX-FileCopyrightText: 2022-2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: WTFPL
.. No warranty

Installation
============

Prerequisites
-------------

You need either `pkgcore`_ or `Portage`_ at runtime to access package manager
functionality, such as filtering by installed packages.

.. _pkgcore: https://pkgcore.github.io/pkgcore/
.. _Portage: https://wiki.gentoo.org/wiki/Project:Portage

Gentoo
------

find-work is packaged for Gentoo in the GURU ebuild repository.

.. prompt:: bash #

   eselect repository enable guru
   emaint sync -r guru
   emerge dev-util/find-work

Manual installation
-------------------

.. prompt:: bash

   pip install gentle-mxml --user

To install manual pages and shell completions, run:

.. prompt:: bash #

   make install-data
