# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Public type definitions for the application, to be used by plugins.
"""

from dataclasses import field
from enum import StrEnum, auto
from itertools import zip_longest

from pydantic import validate_call
from pydantic.dataclasses import dataclass


class VersionPart(StrEnum):
    """
    Enumeration of semver-like version parts.
    """

    #: Major version.
    MAJOR = auto()

    #: Minor version.
    MINOR = auto()

    #: Patch version.
    PATCH = auto()


@dataclass(frozen=True, order=True)
class VersionBump:
    """
    Version bump representation for a Gentoo repository.
    """

    #: Package name.
    atom: str

    #: Outdated version.
    old_version: str = field(compare=False)

    #: Newest available version.
    new_version: str = field(compare=False)

    @validate_call
    def changed(self, stop_after_part: VersionPart) -> bool:
        """
        Roughly determine whether versions differ up to the given part.

        >>> VersionBump("foo", "1.3.2", "1.4").changed(VersionPart.PATCH)
        True
        >>> VersionBump("foo", "1.3.2", "2.0").changed(VersionPart.MINOR)
        True
        >>> VersionBump("foo", "1", "1.0.1").changed(VersionPart.MINOR)
        False
        >>> VersionBump("foo", "1", "1.1").changed(VersionPart.MINOR)
        True

        Remember that it doesn't always work correctly:

        >>> VersionBump("foo", "1", "1.00").changed(VersionPart.MINOR)
        True
        """

        def split_version(version: str) -> list[str]:
            return version.replace("-", ".").replace("_", ".").split(".")

        old_parts = split_version(self.old_version)
        new_parts = split_version(self.new_version)

        parts = list(zip_longest(old_parts, new_parts, fillvalue="0"))
        stop_index = list(VersionPart).index(stop_after_part)
        for old, new in parts[:stop_index + 1]:
            if old != new:
                return True

        return False


@dataclass(frozen=True, order=True)
class BugView:
    """
    Bug listing item representation.
    """

    #: Bug ID.
    bug_id: int

    #: Date this bug was last touched, in ISO format.
    last_change_date: str = field(compare=False)

    #: Assignee of this bug.
    assigned_to: str = field(compare=False)

    #: Summary of this bug.
    summary: str = field(compare=False)
