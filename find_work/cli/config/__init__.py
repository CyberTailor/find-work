# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty.

"""
Apply configuration to the command-line interface.
"""

from collections.abc import Callable
from typing import Any

import click
import pluggy
from click_aliases import ClickAliasedGroup
from pydantic import validate_call

from find_work.cli.config._types import (
    ConfigAlias,
    ConfigAliasCliFlag,
    ConfigAliasCliOption,
    ConfigAliasLiteralValue,
    ConfigAliasValue,
    ConfigRoot,
)
from find_work.cli.options import MainOptions


@validate_call
def _new_click_option(opt_module: str,
                      opt_name: str, opt_obj: ConfigAliasValue) -> Callable:

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


def _callback_from_config(alias_name: str, alias_obj: ConfigAlias, *,
                          plugman: pluggy.PluginManager) -> Callable | None:

    @click.pass_context
    def callback(ctx: click.Context, **kwargs: Any) -> None:
        options: MainOptions = ctx.obj
        opt_module_name, opt_module_obj = alias_obj.options.popitem()
        for opt_name, opt_obj in opt_module_obj.root.items():
            # cli options are processed in their own callbacks
            if isinstance(opt_obj, ConfigAliasLiteralValue):
                options.override(opt_module_name, opt_name, opt_obj.model_dump())

        ctx.invoke(cmd_obj, init_parent=True)

    cmd_obj = plugman.hook.get_command_by_name(command=alias_obj.command)
    if cmd_obj is None:
        return None

    for opt_module in alias_obj.options:
        for opt_name, opt_obj in alias_obj.options[opt_module]:
            decorate_with_option = _new_click_option(opt_module,
                                                     opt_name, opt_obj)
            callback = decorate_with_option(callback)

    callback.__name__ = alias_name
    callback.__doc__ = alias_obj.description
    return callback


def apply_custom_aliases(plugman: pluggy.PluginManager,
                         config: ConfigRoot) -> Callable[[ClickAliasedGroup],
                                                         ClickAliasedGroup]:
    """
    Decorator function to load custom aliases from the configuration.

    :param plugman: Pluggy plugin manager
    :param config: configuration object

    :returns: modified Click group
    """

    def decorator(group: ClickAliasedGroup) -> ClickAliasedGroup:
        for alias_name, alias_obj in config.aliases.items():
            callback = _callback_from_config(alias_name, alias_obj,
                                             plugman=plugman)
            if callback is not None:
                command = click.command(callback)
                group.add_command(command, aliases=alias_obj.shortcuts)
        return group

    return decorator


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
