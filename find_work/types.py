# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Type definitions for the application, implemented (mostly) as Pydantic models.
"""

from dataclasses import field
from enum import Enum, auto

from pydantic.dataclasses import dataclass


@dataclass(frozen=True, order=True)
class VersionBump:
    """ Version bump representation for a Gentoo repository. """

    atom: str
    old_version: str = field(compare=False)
    new_version: str = field(compare=False)


@dataclass(frozen=True, order=True)
class BugView:
    """ Bug listing item representation. """

    bug_id: int
    last_change_date: str = field(compare=False)
    assigned_to: str = field(compare=False)
    summary: str = field(compare=False)


class CliOptionKind(Enum):
    SIMPLE = auto()

    OPTION = auto()
    FLAG = auto()
