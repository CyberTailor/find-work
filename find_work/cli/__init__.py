# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Modules implementing command-line functionality. """

from dataclasses import field

from pydantic.dataclasses import dataclass


@dataclass
class RepologyOptions:
    """ Repology subcommand options. """

    # Repository name
    repo: str = ""


@dataclass
class Options:
    """ Global options. """

    # Enable/disable colors.
    colors: bool | None = None

    # Filter installed packages only
    only_installed: bool = False

    # String used for creating cache key
    cache_key: bytes = b""

    # Repology subcommand options
    repology: RepologyOptions = field(default_factory=RepologyOptions)
