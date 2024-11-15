.. SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: WTFPL
.. No warranty.

Configuration
=============

Files
-----

The `TOML`_ format is used to configure ``find-work``.

.. _TOML: https://toml.io/

The tool reads configuration from the following files, in that order:

* *built-in* (:gitweb:`find_work/app/data/default_config.toml`)
* :file:`/etc/find-work/config.toml`
* :file:`~/.config/find-work/config.toml`

New values are merged with old ones, replacing them on conflicts.

Custom flags
------------

You'll be probably tired typing your email every time with the ``-m`` flag.
Let's add a new command-line flag to make life easier:

.. code-block:: toml

    [flag.larry]
    # This will be the help text for your new global flag
    description = "Only match packages maintained by Larry the Cow."

    # Add some shortcuts to your new global flag. 
    shortcuts = ["-L"]

    # Redefine a global option.
    # Always use the long (double-dash) option name.
    params.maintainer = "larry@gentoo.org"

Save the config file and list bugs assigned to Larry:

.. prompt:: bash

   find-work --larry bugzilla ls

Custom aliases
--------------

You can create new commands from existing ones!

.. code-block:: toml

    [alias.guru-outdated]
    # This will be the help text for your new command.
    description = "Find outdated packages in GURU with Repology."

    # Add some shortcuts to your new command. 
    shortcuts = ["guru-out"]

    # Here we set the target command with "module:command" syntax.
    command = "repology:outdated"

    # And here we pass a static value directly to the internal options.
    options.repology.repo = "gentoo_ovl_guru"

Save the config file and run your new command:

.. prompt:: bash

   find-work -I execute guru-outdated

As you can see, you need to be somewhat familiar with the source code to add new
commands. Happy hacking!
