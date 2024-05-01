# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import os
from datetime import date
from typing import Any

import click
from click_aliases import ClickAliasedGroup

from find_work.cli import Options, apply_custom_flags
from find_work.config import load_config
from find_work.constants import VERSION


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
@apply_custom_flags
def cli(ctx: click.Context, **kwargs: Any) -> None:
    """ Personal advice utility for Gentoo package maintainers. """

    # Process custom global flags
    for flag in load_config().flags:
        if ctx.params[flag.name]:
            for opt, val in flag.params.items():
                ctx.params[opt] = val

    ctx.ensure_object(Options)
    options: Options = ctx.obj

    options.verbose = not ctx.params["quiet"]
    options.only_installed = ctx.params["installed"]
    if any(var in os.environ for var in ["NOCOLOR", "NO_COLOR"]):
        options.colors = False

    options.cache_key.feed(date.today().toordinal())
    if ctx.params["maintainer"]:
        options.maintainer = ctx.params["maintainer"]
        options.cache_key.feed_option("maintainer", options.maintainer)


@cli.group(aliases=["exec", "e"], cls=ClickAliasedGroup)
def execute() -> None:
    """
    Execute a custom command.
    """


find_work.cli.execute.load_aliases(execute)
