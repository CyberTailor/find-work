# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty.

"""
Apply configuration to the command-line interface.
"""

from collections.abc import Callable
from importlib import import_module
from typing import Any

import click
from click_aliases import ClickAliasedGroup

from find_work.cli.config._types import (
    ConfigAlias,
    ConfigAliasCliFlag,
    ConfigAliasCliOption,
    ConfigAliasLiteralValue,
    ConfigAliasValue,
    ConfigFlag,
    ConfigRoot,
)
from find_work.cli.options import MainOptions


def _new_click_option(opt_module: str, opt_name: str,
                      opt_obj: ConfigAliasValue) -> Callable:

    def callback(ctx: click.Context, param: str, value: Any) -> None:
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


def _callback_from_config(alias_name: str, alias_obj: ConfigAlias) -> Callable:

    @click.pass_context
    def callback(ctx: click.Context, **kwargs: Any) -> None:
        cmd_module, cmd_function = alias_obj.command.rsplit(".", maxsplit=1)
        cmd_obj = getattr(import_module(cmd_module), cmd_function)

        options: MainOptions = ctx.obj
        for opt_module in alias_obj.options:
            for opt_name, opt_obj in alias_obj.options[opt_module].root.items():
                # cli options are processed in their own callbacks
                if isinstance(opt_obj, ConfigAliasLiteralValue):
                    options.override(opt_module, opt_name, opt_obj)

        ctx.invoke(cmd_obj)

    for opt_module in alias_obj.options:
        for opt_name, opt_obj in alias_obj.options[opt_module]:
            decorate_with_option = _new_click_option(opt_module, opt_name,
                                                     opt_obj)
            callback = decorate_with_option(callback)

    callback.__name__ = alias_name
    callback.__doc__ = alias_obj.description
    return callback


def load_aliases(group: ClickAliasedGroup, *, config: ConfigRoot) -> None:
    """
    Load custom aliases from the configuration.

    :param group: click group for new commands
    :param config: configuration object
    """

    for alias_name, alias_obj in config.aliases.items():
        callback = _callback_from_config(alias_name, alias_obj)
        add_command = group.command(aliases=alias_obj.shortcuts)
        add_command(callback)


def _global_flag_from_config(flag_name: str, flag_obj: ConfigFlag) -> Callable:

    def callback(ctx: click.Context, param: str, value: Any) -> None:
        if ctx.params[flag_name]:
            for opt, val in flag_obj.params.items():
                ctx.params[opt] = val

    names = {f"--{flag_name}"}
    names |= flag_obj.shortcuts

    return click.option(*names, help=flag_obj.description,
                        callback=callback, is_flag=True)


def apply_custom_flags(config: ConfigRoot) -> Callable[[Callable], Callable]:
    """
    Decorator function to load custom global flags from the configuration.

    :param config: configuration object
    """

    def decorator(callback: Callable) -> Callable:
        for flag_name, flag_obj in config.flags.items():
            decorate_with_option = _global_flag_from_config(flag_name, flag_obj)
            callback = decorate_with_option(callback)
        return callback

    return decorator
