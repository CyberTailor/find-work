# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Type definitions for configuration file.
"""

from enum import Enum, auto


class CliOptionKind(Enum):
    SIMPLE = auto()

    OPTION = auto()
    FLAG = auto()
