# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import os
from datetime import date

import click
from click_aliases import ClickAliasedGroup

import find_work.cli.repology
from find_work.cli import Options
from find_work.constants import VERSION


@click.group(cls=ClickAliasedGroup,
             context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-q", "--quiet", is_flag=True,
              help="Be less verbose.")
@click.option("-I", "--installed", is_flag=True,
              help="Only match installed packages.")
@click.version_option(VERSION, "-V", "--version")
@click.pass_context
def cli(ctx: click.Context, quiet: bool, installed: bool) -> None:
    """ Personal advice utility for Gentoo package maintainers. """

    ctx.ensure_object(Options)
    options: Options = ctx.obj

    options.verbose = not quiet
    options.only_installed = installed
    if any(var in os.environ for var in ["NOCOLOR", "NO_COLOR"]):
        options.colors = False

    today = date.today().toordinal()
    options.cache_key += str(today).encode() + b"\0"


@cli.group(aliases=["rep", "r"], cls=ClickAliasedGroup)
@click.option("-r", "--repo", required=True,
              help="Repository name on Repology.")
@click.pass_obj
def repology(options: Options, repo: str) -> None:
    """ Use Repology to find work. """

    options.repology.repo = repo

    options.cache_key += b"repology" + b"\0"
    options.cache_key += repo.encode() + b"\0"


repology.add_command(find_work.cli.repology.outdated, aliases=["out", "o"])
