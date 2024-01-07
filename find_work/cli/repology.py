# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" CLI subcommands for everything Repology. """

import asyncio
from collections.abc import Iterable

import click
import gentoopm
import repology_client
import repology_client.exceptions
from pydantic import RootModel
from repology_client.types import Package
from sortedcontainers import SortedSet

from find_work.cli import Options
from find_work.types import VersionBump
from find_work.utils import aiohttp_session, read_json_cache, write_json_cache


async def _fetch_outdated(repo: str) -> dict[str, set[Package]]:
    async with aiohttp_session() as session:
        return await repology_client.get_projects(inrepo=repo, outdated="on",
                                                  count=5_000, session=session)


def _projects_from_json(data: dict[str, list]) -> dict[str, set[Package]]:
    result: dict[str, set[Package]] = {}
    for project, packages in data.items():
        result[project] = set()
        for pkg in packages:
            result[project].add(Package(**pkg))
    return result


def _projects_to_json(data: dict[str, set[Package]]) -> dict[str, list]:
    result: dict[str, list] = {}
    for project, packages in data.items():
        result[project] = []
        for pkg in packages:
            pkg_model = RootModel[Package](pkg)
            pkg_dump = pkg_model.model_dump(mode="json", exclude_none=True)
            result[project].append(pkg_dump)
    return result


def _collect_version_bumps(data: Iterable[set[Package]],
                           options: Options) -> SortedSet[VersionBump]:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    result: SortedSet[VersionBump] = SortedSet()
    for packages in data:
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
                result.add(VersionBump(atom,
                                       old_version or "(unknown)",
                                       new_version or "(unknown)"))
    return result


async def _outdated(options: Options) -> None:
    cached_data = read_json_cache(options.cache_key)
    if cached_data is not None:
        data = _projects_from_json(cached_data)
    else:
        try:
            data = await _fetch_outdated(options.repology.repo)
        except repology_client.exceptions.EmptyResponse:
            click.secho("Hmmm, no data returned. Most likely you've made a "
                        "typo in the repository name.",
                        fg="yellow", color=options.colors)
            return
        write_json_cache(_projects_to_json(data), options.cache_key)

    outdated_set = _collect_version_bumps(data.values(), options)
    if len(outdated_set) == 0:
        click.secho("Congrats! You have nothing to do!",
                    fg="green", color=options.colors)
        return

    for bump in outdated_set:
        click.echo(bump.atom + " ", nl=False)
        click.secho(bump.old_version, fg="red", color=options.colors, nl=False)
        click.echo(" → ", nl=False)
        click.secho(bump.new_version, fg="green", color=options.colors)


@click.command()
@click.pass_obj
def outdated(options: Options) -> None:
    """ Find outdated packages. """
    options.cache_key += b"outdated" + b"\0"
    asyncio.run(_outdated(options))
