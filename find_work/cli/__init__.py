# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Modules implementing command-line functionality """

from dataclasses import dataclass, field


@dataclass
class RepologyOptions:
    """ Repology subcommand options """
    repo: str = ""


@dataclass
class Options:
    """ Global options """
    only_installed: bool = False

    repology: RepologyOptions = field(default_factory=RepologyOptions)
