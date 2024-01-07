# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Type definitions for the application, implemented as Pydantic models. """

from dataclasses import field

from pydantic.dataclasses import dataclass


@dataclass(frozen=True, order=True)
class VersionBump:
    """ Version bump representation for a Gentoo repository. """

    atom: str
    old_version: str = field(compare=False)
    new_version: str = field(compare=False)
