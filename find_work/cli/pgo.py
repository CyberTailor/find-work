# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" CLI subcommands for Gentoo Packages website. """

import asyncio

import click
import gentoopm
from pydantic import TypeAdapter
from sortedcontainers import SortedDict, SortedSet
from tabulate import tabulate

from find_work.cache import (
    read_raw_json_cache,
    write_raw_json_cache,
)
from find_work.cli import (
    Message,
    Options,
    ProgressDots,
)
from find_work.constants import (
    PGO_BASE_URL,
    PGO_API_URL,
)
from find_work.types import (
    VersionBump,
    VersionPart,
)
from find_work.types._pgo import (
    GraphQlResponse,
    OutdatedPackage,
    PkgCheckResult,
    StableCandidate,
)
from find_work.utils import aiohttp_session

OutdatedPackageSet = frozenset[OutdatedPackage]
PkgCheckResultSet = frozenset[PkgCheckResult]
StableCandidateSet = frozenset[StableCandidate]


async def _fetch_outdated() -> OutdatedPackageSet:
    query = """query {
        outdatedPackages{
            Atom
            GentooVersion
            NewestVersion
        }
    }"""

    async with aiohttp_session() as session:
        async with session.post(PGO_API_URL, json={"query": query},
                                raise_for_status=True) as response:
            raw_data = await response.read()

    graphql = GraphQlResponse.model_validate_json(raw_data)
    return graphql.data.outdated


def _collect_version_bumps(data: OutdatedPackageSet,
                           options: Options) -> SortedSet[VersionBump]:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    result: SortedSet[VersionBump] = SortedSet()
    for item in data:
        if options.only_installed and item.atom not in pm.installed:
            continue
        result.add(item.as_version_bump)
    return result


async def _outdated(options: Options) -> None:
    if options.maintainer:
        raise NotImplementedError(
            "Filtering by maintainer is not implemented for this command"
        )

    if (extra_options := options.pgo.extra_options) is not None:
        version_part: VersionPart | None = extra_options.get("version_part")

    dots = ProgressDots(options.verbose)

    options.say(Message.CACHE_LOAD)
    with dots():
        raw_data = read_raw_json_cache(options.cache_key)
    if raw_data:
        options.say(Message.CACHE_READ)
        with dots():
            data = TypeAdapter(OutdatedPackageSet).validate_json(raw_data)
    else:
        options.vecho("Fetching data from Gentoo Packages API",
                      nl=False, err=True)
        with dots():
            data = await _fetch_outdated()
        if len(data) == 0:
            options.say(Message.EMPTY_RESPONSE)
            return
        options.say(Message.CACHE_WRITE)
        with dots():
            raw_json = TypeAdapter(OutdatedPackageSet).dump_json(
                data, by_alias=True, exclude_none=True
            )
            write_raw_json_cache(raw_json, options.cache_key)

    no_work = True
    for bump in _collect_version_bumps(data, options):
        if version_part and not bump.changed(version_part):
            continue

        options.echo(bump.atom + " ", nl=False)
        options.secho(bump.old_version, fg="red", nl=False)
        options.echo(" → ", nl=False)
        options.secho(bump.new_version, fg="green")
        no_work = False

    if no_work:
        options.say(Message.NO_WORK)


async def _fetch_maintainer_stabilization(maintainer: str) -> PkgCheckResultSet:

    url = PGO_BASE_URL + f"/maintainer/{maintainer}/stabilization.json"
    async with aiohttp_session() as session:
        async with session.get(url, raise_for_status=True) as response:
            raw_data = await response.read()

    data = TypeAdapter(StableCandidateSet).validate_json(raw_data)
    return frozenset(item.as_pkgcheck_result for item in data)


async def _fetch_all_stabilization() -> PkgCheckResultSet:
    query = """query {
        pkgCheckResults(Class: "StableRequest") {
            Atom
            Version
            Message
        }
    }"""

    async with aiohttp_session() as session:
        async with session.post(PGO_API_URL, json={"query": query},
                                raise_for_status=True) as response:
            raw_data = await response.read()

    graphql = GraphQlResponse.model_validate_json(raw_data)
    return graphql.data.pkgcheck


async def _fetch_stabilization(options: Options) -> PkgCheckResultSet:
    if options.maintainer:
        return await _fetch_maintainer_stabilization(options.maintainer)
    return await _fetch_all_stabilization()


def _collect_stable_candidates(data: PkgCheckResultSet,
                               options: Options) -> SortedDict[str, str]:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    result: SortedDict[str, str] = SortedDict()
    for item in data:
        if options.only_installed and item.atom not in pm.installed:
            continue
        key = "-".join([item.atom, item.version])
        result[key] = item.message
    return result


async def _stabilization(options: Options) -> None:
    dots = ProgressDots(options.verbose)

    options.say(Message.CACHE_LOAD)
    with dots():
        raw_data = read_raw_json_cache(options.cache_key)
    if raw_data:
        options.say(Message.CACHE_READ)
        with dots():
            data = TypeAdapter(PkgCheckResultSet).validate_json(raw_data)
    else:
        options.vecho("Fetching data from Gentoo Packages API",
                      nl=False, err=True)
        with dots():
            data = await _fetch_stabilization(options)
        if len(data) == 0:
            options.say(Message.EMPTY_RESPONSE)
            return
        options.say(Message.CACHE_WRITE)
        with dots():
            raw_data = TypeAdapter(PkgCheckResultSet).dump_json(
                data, by_alias=True, exclude_none=True
            )
            write_raw_json_cache(raw_data, options.cache_key)

    candidates = _collect_stable_candidates(data, options)
    if len(candidates) != 0:
        options.echo(tabulate(candidates.items(), tablefmt="plain"))
    else:
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

    options.pgo.extra_options = {"version_part": version_part}
    asyncio.run(_outdated(options))


@click.command()
@click.pass_obj
def stabilization(options: Options) -> None:
    """
    Find stable candidates.
    """

    options.cache_key.feed("stabilization")
    asyncio.run(_stabilization(options))
