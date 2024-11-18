# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Public type definitions for the application.
"""

from enum import StrEnum, auto


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
