# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" CLI subcommand for executing custom aliases. """

import tomllib
from collections.abc import Callable
from importlib import import_module
from importlib.resources import files
from pathlib import Path
from typing import Any

import click
import gentoopm
from click_aliases import ClickAliasedGroup
from deepmerge import always_merger
from platformdirs import PlatformDirs

import find_work.data
from find_work.cli import Options
from find_work.config import Config, ConfigAlias, ConfigModuleOption
from find_work.constants import DEFAULT_CONFIG, ENTITY, PACKAGE
from find_work.types import CliOptionKind


def _new_click_option(opt: ConfigModuleOption) -> Callable:

    def callback(ctx: click.Context, param: str, value: Any) -> None:
        options: Options = ctx.obj
        options[opt.module][opt.name] = value

    is_flag: bool = False
    match opt.kind:
        case CliOptionKind.OPTION:
            is_flag = False
        case CliOptionKind.FLAG:
            is_flag = True
        case _:
            # dumb wrapper
            return lambda f: f

    return click.option(*opt.value, callback=callback, is_flag=is_flag)


def _callback_from_config(alias: ConfigAlias) -> Callable:

    @click.pass_context
    def callback(ctx: click.Context, **kwargs: Any) -> None:
        cmd_module, cmd_function = alias.command.rsplit(".", maxsplit=1)
        cmd_group = cmd_module.rsplit(".", maxsplit=1)[-1]
        cmd_obj = getattr(import_module(cmd_module), cmd_function)

        options: Options = ctx.obj
        for opt in alias.options:
            # cli options are processed in their own callbacks
            if opt.kind == CliOptionKind.SIMPLE:
                options[opt.module][opt.name] = opt.value

        options.cache_key.feed(cmd_group)
        for key in options[cmd_group].cache_order:
            options.cache_key.feed_option(key, options[cmd_group][key])
        ctx.invoke(cmd_obj)

    for opt in alias.options:
        callback = _new_click_option(opt)(callback)
    callback.__name__ = alias.name
    callback.__doc__ = alias.description
    return callback


def load_aliases(group: ClickAliasedGroup) -> None:
    """
    Load custom aliases from configuration files.

    :param group: click group for new commands
    """

    default_config = files(find_work.data).joinpath(DEFAULT_CONFIG).read_text()
    toml = tomllib.loads(default_config)

    pm = gentoopm.get_package_manager()
    system_config = Path(pm.root) / "etc" / PACKAGE / "config.toml"
    if system_config.is_file():
        with open(system_config, "rb") as file:
            always_merger.merge(toml, tomllib.load(file))

    dirs = PlatformDirs(PACKAGE, ENTITY, roaming=True)
    user_config = dirs.user_config_path / "config.toml"
    if user_config.is_file():
        with open(user_config, "rb") as file:
            always_merger.merge(toml, tomllib.load(file))

    config = Config(toml)
    for alias in config.aliases:
        group.command(aliases=alias.shortcuts)(_callback_from_config(alias))
