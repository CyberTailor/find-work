# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty.

"""
Loadable plug-in interface.
"""

import click
import pluggy
from click_aliases import ClickAliasedGroup

from find_work.cli.options import MainOptions
from find_work.constants import PACKAGE

hook_spec = pluggy.HookspecMarker(PACKAGE)
hook_impl = pluggy.HookimplMarker(PACKAGE)


class PluginSpec:
    """
    Specifications of CLI plugin hooks.
    """

    @hook_spec
    def attach_base_command(self, group: ClickAliasedGroup) -> None:
        """
        Attach plugin's base command to the CLI.

        :param group: Click group
        """

    @hook_spec
    def setup_base_command(self, options: MainOptions) -> None:
        """
        Initialize plugin's base command.

        This hook should not change the global state.

        :param options: global options
        """

    @hook_spec(firstresult=True)
    def get_command_by_name(self, command: str) -> click.Command | None:
        """
        Match a command by its name.

        :param command: colon-separated pair of plugin name and command name to
                        match, without any whitespace

        :returns: matched command or ``None``
        """


__all__ = [
    "hook_impl",
    "PluginSpec",
]
