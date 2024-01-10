# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import os
from datetime import date

import click
from click_aliases import ClickAliasedGroup

import find_work.cli.bugzilla
import find_work.cli.pgo
import find_work.cli.repology
from find_work.cli import Options
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
def cli(ctx: click.Context, maintainer: str | None,
        quiet: bool, installed: bool) -> None:
    """ Personal advice utility for Gentoo package maintainers. """

    ctx.ensure_object(Options)
    options: Options = ctx.obj

    options.verbose = not quiet
    options.only_installed = installed
    if any(var in os.environ for var in ["NOCOLOR", "NO_COLOR"]):
        options.colors = False

    options.cache_key.feed(date.today().toordinal())
    if maintainer:
        options.maintainer = maintainer
        options.cache_key.feed(maintainer=maintainer)


@cli.group(aliases=["bug", "b"], cls=ClickAliasedGroup)
@click.option("-c", "--component", metavar="NAME",
              help="Component name on Bugzilla.")
@click.option("-p", "--product", metavar="NAME",
              help="Product name on Bugzilla.")
@click.option("-t", "--time", is_flag=True,
              help="Sort bugs by time last modified.")
@click.pass_obj
def bugzilla(options: Options, component: str | None, product: str | None,
             time: bool) -> None:
    """ Use Bugzilla to find work. """

    options.bugzilla.chronological_sort = time

    options.cache_key.feed("bugzilla")
    options.cache_key.feed(time=time)

    if product:
        options.bugzilla.product = product
        options.cache_key.feed(product=product)
    if component:
        options.bugzilla.component = component
        options.cache_key.feed(component=component)


@cli.group(aliases=["p"], cls=ClickAliasedGroup)
@click.pass_obj
def pgo(options: Options) -> None:
    """ Use Gentoo Packages website to find work. """

    options.cache_key.feed("pgo")


@cli.group(aliases=["rep", "r"], cls=ClickAliasedGroup)
@click.option("-r", "--repo", metavar="NAME", required=True,
              help="Repository name on Repology.")
@click.pass_obj
def repology(options: Options, repo: str) -> None:
    """ Use Repology to find work. """

    options.repology.repo = repo
    options.cache_key.feed("repology", repo)


bugzilla.add_command(find_work.cli.bugzilla.outdated, aliases=["out", "o"])

pgo.add_command(find_work.cli.pgo.outdated, aliases=["out", "o"])
pgo.add_command(find_work.cli.pgo.stabilization, aliases=["stab", "s"])

repology.add_command(find_work.cli.repology.outdated, aliases=["out", "o"])
