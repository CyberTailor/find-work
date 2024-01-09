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

from find_work.cli import Options, ProgressDots
from find_work.types import VersionBump
from find_work.utils import (
    aiohttp_session,
    read_json_cache,
    write_json_cache,
)


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

    options.vecho("Checking for cached data", nl=False, err=True)
    with dots():
        cached_data = read_json_cache(options.cache_key)
    if cached_data is not None:
        options.vecho("Loading cached data", nl=False, err=True)
        with dots():
            data = _projects_from_json(cached_data)
    else:
        try:
            options.vecho("Fetching data from Repology API", nl=False, err=True)
            with dots():
                data = await _fetch_outdated(options.repology.repo)
        except repology_client.exceptions.EmptyResponse:
            options.secho("Hmmm, no data returned. Most likely you've made a "
                          "typo in the repository name.", fg="yellow")
            return
        options.vecho("Caching data", nl=False, err=True)
        with dots():
            json_data = _projects_to_json(data)
            write_json_cache(json_data, options.cache_key)

    outdated_set = _collect_version_bumps(data.values(), options)
    if len(outdated_set) == 0:
        options.secho("Congrats! You have nothing to do!", fg="green")
        return

    for bump in outdated_set:
        options.echo(bump.atom + " ", nl=False)
        options.secho(bump.old_version, fg="red", nl=False)
        options.echo(" → ", nl=False)
        options.secho(bump.new_version, fg="green")


@click.command()
@click.pass_obj
def outdated(options: Options) -> None:
    """ Find outdated packages. """
    options.cache_key += b"outdated" + b"\0"
    asyncio.run(_outdated(options))
