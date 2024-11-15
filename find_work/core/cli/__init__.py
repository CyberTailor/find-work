# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Command line functionality.
"""

import os


def colors_disabled_by_env() -> bool:
    """
    Check whether the user explicitly told to disable colors.

    This function checks whether one of the environment variables — ``NO_COLOR``
    or ``NOCOLOR`` — is defined and is not an empty string.

    See also: https://no-color.org/

    :returns: whether to disable colors
    """

    return any(os.environ.get(var) for var in ["NO_COLOR", "NOCOLOR"])
