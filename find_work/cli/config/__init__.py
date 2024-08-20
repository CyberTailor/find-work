# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty.

"""
Apply configuration to the command-line interface.
"""

from collections.abc import Callable
from typing import Any, NoReturn

import click
import pluggy
from click_aliases import ClickAliasedGroup
from pydantic import validate_call

from find_work.cli.config._types import (
    ConfigAliasCliFlag,
    ConfigAliasCliOption,
    ConfigAliasLiteralValue,
    ConfigAliasValue,
    ConfigRoot,
)
from find_work.cli.options import MainOptions


@validate_call
def apply_custom_flags(config: ConfigRoot) -> Callable[[ClickAliasedGroup],
                                                       ClickAliasedGroup]:
    """
    Decorator function to load custom global flags from the configuration.

    :param config: configuration object

    :returns: modified Click group
    """

    def decorator(group: ClickAliasedGroup) -> ClickAliasedGroup:
        for flag_name, flag_obj in config.flags.items():
            names = {f"--{flag_name}"}
            names |= flag_obj.shortcuts

            decorate_with_option = click.option(*names,
                                                help=flag_obj.description,
                                                is_flag=True)
            group = decorate_with_option(group)
        return group

    return decorator


class ClickExecutorGroup(click.Group):
    """
    Lazy-load load custom aliases from the configuration.
    """

    def __init__(self, *args: Any, plugman: pluggy.PluginManager,
                 config: ConfigRoot, **kwargs: Any):
        """
        :param plugman: Pluggy plugin manager
        :param config: configuration object
        """

        super().__init__(*args, **kwargs)
        self._plugin_manager = plugman
        self._config = config

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted(self._config.aliases.keys())

    def get_command(self, ctx: click.Context,
                    cmd_name: str) -> click.Command | None:
        if (alias_name := self._resolve_shortcut(cmd_name)) is not None:
            callback = self._callback_from_config(alias_name)
            if callback is not None:
                return click.command(callback)
        return None

    def format_commands(self, ctx: click.Context,
                        formatter: click.HelpFormatter) -> None:
        max_len: int = 0
        if len(self._config.aliases) > 0:
            max_len = max(len(cmd) for cmd in self._config.aliases)

        limit: int = formatter.width - 6 - max_len
        rows: list[tuple[str, str]] = []
        for alias_name in self.list_commands(ctx):
            alias_obj = self._config.aliases[alias_name]
            subcommand: str = alias_name
            if alias_obj.shortcuts:
                shortcuts = ",".join(sorted(alias_obj.shortcuts))
                subcommand = f"{alias_name} ({shortcuts})"
            cmd_help = alias_obj.description[:limit]
            rows.append((subcommand, cmd_help))

        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)

    def add_command(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise NotImplementedError

    def command(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise NotImplementedError

    def group(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise NotImplementedError

    @validate_call(validate_return=True)
    def _resolve_shortcut(self, cmd_name: str) -> str | None:
        if cmd_name in self._config.aliases:
            return cmd_name

        for alias_name, alias_obj in self._config.aliases.items():
            if cmd_name in alias_obj.shortcuts:
                return alias_name

        return None

    @staticmethod
    @validate_call
    def _new_click_option(opt_module: str, opt_name: str,
                          opt_obj: ConfigAliasValue) -> Callable:

        def callback(ctx: click.Context, param: click.Option, value: Any) -> None:
            options: MainOptions = ctx.obj
            options.override(opt_module, opt_name, value)

        is_flag: bool = False
        match opt_obj:
            case ConfigAliasCliOption():
                is_flag = False
            case ConfigAliasCliFlag():
                is_flag = True
            case _:
                # dumb wrapper
                return lambda f: f

        return click.option(*opt_obj.names, callback=callback, is_flag=is_flag)

    @validate_call
    def _callback_from_config(self, alias_name: str) -> Callable | None:

        @click.pass_context
        def callback(ctx: click.Context, **kwargs: Any) -> None:
            options: MainOptions = ctx.obj
            for opt_name, opt_obj in opt_module_obj.root.items():
                # cli options are processed in their own callbacks
                if isinstance(opt_obj, ConfigAliasLiteralValue):
                    options.override(opt_module_name, opt_name, opt_obj.model_dump())

            ctx.invoke(cmd_obj, init_parent=True)

        alias_obj = self._config.aliases[alias_name]
        cmd_obj = self._plugin_manager.hook.get_command_by_name(
            command=alias_obj.command
        )
        if cmd_obj is None:
            return None

        opt_module_name, opt_module_obj = next(
            iter(alias_obj.options.items())
        )
        for opt_name, opt_obj in opt_module_obj.root.items():
            decorate_with_option = self._new_click_option(opt_module_name,
                                                          opt_name, opt_obj)
            callback = decorate_with_option(callback)

        callback.__name__ = alias_name
        callback.__doc__ = alias_obj.description
        return callback
