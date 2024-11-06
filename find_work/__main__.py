# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import functools
import tomllib
from datetime import date
from importlib.resources import files
from pathlib import Path

import click
import pluggy
from deepmerge import always_merger
from platformdirs import PlatformDirs

import find_work.data
from find_work.cli import colors_disabled_by_env
from find_work.cli.config import (
    ClickCustomFlagsGroup,
    ClickExecutorGroup,
)
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
    plugman.load_setuptools_entrypoints("find_work.plugins")

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

    system_config = Path("/etc") / PACKAGE / "config.toml"
    if system_config.is_file():
        with open(system_config, "rb") as file:
            always_merger.merge(toml, tomllib.load(file))

    dirs = PlatformDirs(PACKAGE, ENTITY, roaming=True)
    user_config = dirs.user_config_path / "config.toml"
    if user_config.is_file():
        with open(user_config, "rb") as file:
            always_merger.merge(toml, tomllib.load(file))

    return ConfigRoot.model_validate(toml)


@click.group(cls=ClickCustomFlagsGroup, config=load_config(),
             context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-m", "--maintainer", metavar="EMAIL",
              help="Filter by package maintainer.")
@click.option("-q", "--quiet", is_flag=True,
              help="Be less verbose.")
@click.option("-I", "--installed", is_flag=True,
              help="Only match installed packages.")
@click.version_option(VERSION, "-V", "--version")
@click.pass_context
def cli(ctx: click.Context, maintainer: str | None, quiet: bool = False,
        installed: bool = False) -> None:
    """
    Personal advice utility for Gentoo package maintainers.

    See `man find-work` for the full help.
    """

    ctx.ensure_object(MainOptions)
    options: MainOptions = ctx.obj

    options.verbose = not quiet
    options.only_installed = installed
    if colors_disabled_by_env():
        options.colors = False

    options.breadcrumbs.feed(date.today().toordinal())
    if maintainer:
        options.maintainer = maintainer
        options.breadcrumbs.feed_option("maintainer", options.maintainer)

    get_plugin_manager().hook.setup_base_command(options=options)


@cli.group(aliases=["exec", "e"], cls=ClickExecutorGroup,
           plugman=get_plugin_manager(), config=load_config())
def execute() -> None:
    """
    Execute a custom command.
    """


get_plugin_manager().hook.attach_base_command(group=cli)
