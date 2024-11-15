# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty.

"""
Loadable plug-in interface.
"""

import click
import pluggy
from click_aliases import ClickAliasedGroup

from find_work.core.cli.options import MainOptions
from find_work.core.constants import PACKAGE

cli_hook_spec = pluggy.HookspecMarker(PACKAGE)
cli_hook_impl = pluggy.HookimplMarker(PACKAGE)


class PluginSpec:
    """
    Specifications of CLI plugin hooks.
    """

    @cli_hook_spec
    def attach_base_command(self, group: ClickAliasedGroup) -> None:
        """
        Attach plugin's base command to the CLI.

        :param group: Click group
        """

    @cli_hook_spec
    def setup_base_command(self, options: MainOptions) -> None:
        """
        Initialize plugin's base command.

        This hook should not change the global state.

        :param options: global options
        """

    @cli_hook_spec(firstresult=True)
    def get_command_by_name(self, command: str) -> click.Command | None:
        """
        Match a command by its name.

        :param command: colon-separated pair of plugin name and command name to
                        match, without any whitespace

        :returns: matched command or ``None``
        """


__all__ = [
    "cli_hook_impl",
    "PluginSpec",
]
