# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" CLI subcommands for everything Repology. """

import asyncio
from collections.abc import Collection

import click
import gentoopm
import repology_client
import repology_client.exceptions
from gentoopm.basepm.atom import PMAtom
from pydantic import TypeAdapter
from repology_client.types import Package
from sortedcontainers import SortedSet

from find_work.cache import (
    read_raw_json_cache,
    write_raw_json_cache,
)
from find_work.cli import Message, Options, ProgressDots
from find_work.types import VersionBump, VersionPart
from find_work.utils import aiohttp_session

PackageSet = set[Package]
ProjectsMapping = dict[str, PackageSet]


async def _fetch_outdated(options: Options) -> ProjectsMapping:
    filters: dict = {}
    if options.maintainer:
        filters["maintainer"] = options.maintainer

    async with aiohttp_session() as session:
        return await repology_client.get_projects(inrepo=options.repology.repo,
                                                  outdated="on", count=5_000,
                                                  session=session, **filters)


def _collect_version_bumps(data: Collection[PackageSet],
                           options: Options) -> SortedSet[VersionBump]:
    pm = gentoopm.get_package_manager()

    result: SortedSet[VersionBump] = SortedSet()
    for packages in data:
        latest_pkgs: dict[str, PMAtom] = {}  # latest in repo, not across repos!
        new_version: str | None = None

        for pkg in packages:
            if pkg.status == "outdated" and pkg.repo == options.repology.repo:
                # "pkg.version" can contain spaces, better avoid it!
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

    if (extra_options := options.repology.extra_options) is not None:
        version_part: VersionPart | None = extra_options.get("version_part")

    options.say(Message.CACHE_LOAD)
    with dots():
        raw_data = read_raw_json_cache(options.cache_key)
    if raw_data:
        options.say(Message.CACHE_READ)
        with dots():
            data = TypeAdapter(ProjectsMapping).validate_json(raw_data)
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
            raw_json = TypeAdapter(ProjectsMapping).dump_json(
                data, exclude_none=True
            )
            write_raw_json_cache(raw_json, options.cache_key)

    no_work = True
    for bump in _collect_version_bumps(data.values(), options):
        if version_part and not bump.changed(version_part):
            continue

        options.echo(bump.atom + " ", nl=False)
        options.secho(bump.old_version, fg="red", nl=False)
        options.echo(" → ", nl=False)
        options.secho(bump.new_version, fg="green")
        no_work = False

    if no_work:
        options.say(Message.NO_WORK)


@click.command()
@click.option("-F", "--filter", "version_part",
              type=click.Choice(["major", "minor", "patch"]),
              help="Version part filter.")
@click.pass_obj
def outdated(options: Options, version_part: VersionPart | None = None) -> None:
    """
    Find outdated packages.
    """

    options.cache_key.feed("outdated")

    options.repology.extra_options = {"version_part": version_part}
    asyncio.run(_outdated(options))
