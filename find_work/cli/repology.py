# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" CLI subcommands for everything Repology. """

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import field

import aiohttp
import click
import gentoopm
import repology_client
import repology_client.exceptions
from pydantic.dataclasses import dataclass
from sortedcontainers import SortedSet

from find_work.cli import Options
from find_work.constants import USER_AGENT


@dataclass(frozen=True, order=True)
class VersionBump:
    """ Version bump representation for a Gentoo repository. """

    atom: str
    old_version: str = field(compare=False)
    new_version: str = field(compare=False)


@asynccontextmanager
async def aiohttp_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """
    Construct an :external+aiohttp:py:class:`aiohttp.ClientSession` object.
    """
    headers = {"user-agent": USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=30)
    session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    yield session
    await session.close()


async def _outdated(options: Options) -> None:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    async with aiohttp_session() as session:
        try:
            data = await repology_client.get_projects(inrepo=options.repology.repo,
                                                      outdated="on", count=5_000,
                                                      session=session)
        except repology_client.exceptions.EmptyResponse:
            click.secho("Hmmm, no data returned. Most likely you've made a "
                        "typo in repository name.", fg="yellow")
            return

    outdated_set: SortedSet[VersionBump] = SortedSet()
    for packages in data.values():
        atom: str | None = None
        old_version: str | None = None
        new_version: str | None = None

        for pkg in packages:
            if atom and old_version and new_version:
                break

            if pkg.repo == options.repology.repo:
                atom = pkg.visiblename
                old_version = pkg.version
            elif pkg.status == "newest":
                new_version = pkg.version

        if atom is not None:
            if not (options.only_installed and atom not in pm.installed):
                outdated_set.add(VersionBump(atom,
                                             old_version or "(unknown)",
                                             new_version or "(unknown)"))

    if len(outdated_set) == 0:
        click.secho("Congrats! You have nothing to do!", fg="green")
        return

    for bump in outdated_set:
        click.echo(bump.atom + " ", nl=False)
        click.secho(bump.old_version or "(unknown)", fg="red", nl=False)
        click.echo(" → ", nl=False)
        click.secho(bump.new_version or "(unknown)", fg="green")


@click.command()
@click.pass_obj
def outdated(options: Options) -> None:
    """ Find outdated packages. """
    asyncio.run(_outdated(options))
