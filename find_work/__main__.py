# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

from typing import Callable

import click
from click_aliases import ClickAliasedGroup

import find_work
import find_work.cli.repology
from find_work.cli import Options


def help_text(docstring: str) -> Callable:
    """
    Override function's docstring.

    :param docstring: new docstring
    :return: decorated function
    """
    def decorate(f: Callable) -> Callable:
        f.__doc__ = docstring
        return f
    return decorate


@click.group(cls=ClickAliasedGroup,
             context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-I", "--installed", is_flag=True,
              help="Only match installed packages.")
@click.version_option(find_work.__version__, "-V", "--version")
@click.pass_context
@help_text(find_work.__doc__)
def cli(ctx: click.Context, installed: bool) -> None:
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
