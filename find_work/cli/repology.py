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
from gentoopm.basepm.atom import PMAtom
from pydantic import RootModel
from repology_client.types import Package
from sortedcontainers import SortedSet

from find_work.cli import Message, Options, ProgressDots
from find_work.types import VersionBump
from find_work.utils import (
    aiohttp_session,
    read_json_cache,
    write_json_cache,
)


async def _fetch_outdated(options: Options) -> dict[str, set[Package]]:
    filters: dict = {}
    if options.maintainer:
        filters["maintainer"] = options.maintainer

    async with aiohttp_session() as session:
        return await repology_client.get_projects(inrepo=options.repology.repo,
                                                  outdated="on", count=5_000,
                                                  session=session, **filters)


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
    pm = gentoopm.get_package_manager()

    result: SortedSet[VersionBump] = SortedSet()
    for packages in data:
        latest_pkgs: dict[str, PMAtom] = {}  # latest in repo, not across repos!
        new_version: str | None = None

        for pkg in packages:
            if pkg.status == "outdated" and pkg.repo == options.repology.repo:
                # ``pkg.version`` can contain spaces, better avoid it!
                origversion = pkg.origversion or pkg.version
                atom = pm.Atom(f"={pkg.visiblename}-{origversion}")

                latest = latest_pkgs.get(pkg.visiblename)
                if latest is None or atom.version > latest.version:
                    latest_pkgs[pkg.visiblename] = atom
            elif pkg.status == "newest":
                new_version = pkg.version

        for latest in latest_pkgs.values():
            if not (options.only_installed and latest.key not in pm.installed):
                result.add(VersionBump(str(latest.key), str(latest.version),
                                       new_version or "(unknown)"))
    return result


async def _outdated(options: Options) -> None:
    dots = ProgressDots(options.verbose)

    options.say(Message.CACHE_LOAD)
    with dots():
        cached_data = read_json_cache(options.cache_key)
    if cached_data is not None:
        options.say(Message.CACHE_READ)
        with dots():
            data = _projects_from_json(cached_data)
    else:
        options.vecho("Fetching data from Repology API", nl=False, err=True)
        try:
            with dots():
                data = await _fetch_outdated(options)
        except repology_client.exceptions.EmptyResponse:
            options.say(Message.EMPTY_RESPONSE)
            return
        options.say(Message.CACHE_WRITE)
        with dots():
            json_data = _projects_to_json(data)
            write_json_cache(json_data, options.cache_key)

    outdated_set = _collect_version_bumps(data.values(), options)
    for bump in outdated_set:
        options.echo(bump.atom + " ", nl=False)
        options.secho(bump.old_version, fg="red", nl=False)
        options.echo(" → ", nl=False)
        options.secho(bump.new_version, fg="green")

    if len(outdated_set) == 0:
        options.say(Message.NO_WORK)


@click.command()
@click.pass_obj
def outdated(options: Options) -> None:
    """ Find outdated packages. """
    options.cache_key.feed("outdated")
    asyncio.run(_outdated(options))
