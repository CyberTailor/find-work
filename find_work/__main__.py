# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import click
from click_aliases import ClickAliasedGroup

import find_work.cli.repology
from find_work.cli import Options
from find_work.constants import VERSION


@click.group(cls=ClickAliasedGroup,
             context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-I", "--installed", is_flag=True,
              help="Only match installed packages.")
@click.version_option(VERSION, "-V", "--version")
@click.pass_context
def cli(ctx: click.Context, installed: bool) -> None:
    """ Personal advice utility for Gentoo package maintainers. """
    ctx.ensure_object(Options)
    ctx.obj.only_installed = installed


@cli.group(aliases=["rep", "r"], cls=ClickAliasedGroup)
@click.option("-r", "--repo", required=True,
              help="Repository name on Repology.")
@click.pass_obj
def repology(options: Options, repo: str) -> None:
    """ Use Repology to find work. """
    options.repology.repo = repo


repology.add_command(find_work.cli.repology.outdated, aliases=["out", "o"])
