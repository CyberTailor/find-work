# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import functools
import tomllib
from datetime import date
from importlib.resources import files
from pathlib import Path
from typing import Any

import click
import gentoopm
import pluggy
from click_aliases import ClickAliasedGroup
from deepmerge import always_merger
from platformdirs import PlatformDirs

import find_work.data
from find_work.cli import colors_disabled_by_env
from find_work.cli.config import apply_custom_aliases, apply_custom_flags
from find_work.cli.config._types import ConfigRoot
from find_work.cli.options import MainOptions
from find_work.cli.plugins import PluginSpec
from find_work.constants import (
    DEFAULT_CONFIG,
    ENTITY,
    PACKAGE,
    VERSION,
)


@functools.cache
def get_plugin_manager() -> pluggy.PluginManager:
    """
    Load plug-ins from entry points.

    Calls to this functions are cached.

    :returns: plugin manager instance
    """

    plugman = pluggy.PluginManager(PACKAGE)
    plugman.add_hookspecs(PluginSpec)
    plugman.load_setuptools_entrypoints(PACKAGE)

    return plugman


@functools.cache
def load_config() -> ConfigRoot:
    """
    Load configuration files.

    Calls to this functions are cached.

    :returns: parsed config
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

    return ConfigRoot.model_validate(toml)


@click.group(cls=ClickAliasedGroup,
             context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-m", "--maintainer", metavar="EMAIL",
              help="Filter by package maintainer.")
@click.option("-q", "--quiet", is_flag=True,
              help="Be less verbose.")
@click.option("-I", "--installed", is_flag=True,
              help="Only match installed packages.")
@click.version_option(VERSION, "-V", "--version")
@click.pass_context
@apply_custom_flags(load_config())
def cli(ctx: click.Context, **kwargs: Any) -> None:
    """
    Personal advice utility for Gentoo package maintainers.
    """

    # Process custom global flags
    for flag_name, flag_obj in load_config().flags.items():
        if ctx.params[flag_name]:
            for opt, val in flag_obj.params.items():
                ctx.params[opt] = val

    ctx.ensure_object(MainOptions)
    options: MainOptions = ctx.obj

    options.verbose = not ctx.params["quiet"]
    options.only_installed = ctx.params["installed"]
    if colors_disabled_by_env():
        options.colors = False

    options.breadcrumbs.feed(date.today().toordinal())
    if ctx.params["maintainer"]:
        options.maintainer = ctx.params["maintainer"]
        options.breadcrumbs.feed_option("maintainer", options.maintainer)

    get_plugin_manager().hook.setup_base_command(options=options)


@apply_custom_aliases(get_plugin_manager(), load_config())
@cli.group(aliases=["exec", "e"], cls=ClickAliasedGroup)
def execute() -> None:
    """
    Execute a custom command.
    """


get_plugin_manager().hook.attach_base_command(group=cli)
