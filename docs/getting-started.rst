.. SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: WTFPL
.. No warranty.

Getting Started
===============

Basic usage
-----------

To discover, which outdated packages in GURU are installed on your system, run:

.. prompt:: bash

   find-work -I repology -r gentoo_ovl_guru outdated

.. tip::

   * ``-I`` flag is a filter to display installed packages only. Global flags
     must precede module name.
   * ``repology`` is a module. Every data source is in its own module.
   * ``-r <repo>`` specifies repository name on Repology. Module flags
     must precede command name.
   * ``outdated`` is a command in the ``repology`` module.

   .. seealso:: :manpage:`find-work.1` manual page

You can use command aliases, for example:

.. prompt:: bash

   find-work -I rep -r gentoo_ovl_guru out

All data from APIs is cached for a day, so don't hesitate running the command
again and again!

Custom aliases
--------------

You can create new commands from existing ones!

To start, launch your favorite editor at :file:`~/.config/find-work/config.toml`
and write your first alias:

.. code-block:: toml

    [alias.guru-outdated]
    # This will be the help text for your new command.
    description = "Find outdated packages in GURU with Repology."

    # Add some shortcuts to your new command. 
    shortcuts = ["guru-out"]

    # Here we set the target command with Python syntax.
    command = "find_work.cli.repology.outdated"

    # And here we pass a static value directly to the internal options.
    options.repology.repo = "gentoo_ovl_guru"

Save the config file and run your new command:

.. prompt:: bash

   find-work -I execute guru-outdated

As you can see, you need to be somewhat familiar with the utility's source code.
Happy hacking!

.. tip::

   See :gitweb:`find_work/data/default_config.toml` for pre-defined aliases.
