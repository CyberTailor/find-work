# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" CLI subcommands for Gentoo Packages website. """

import asyncio
from collections.abc import Iterable

import click
import gentoopm
from sortedcontainers import SortedDict, SortedSet
from tabulate import tabulate

from find_work.cli import Message, Options, ProgressDots
from find_work.constants import PGO_BASE_URL, PGO_API_URL
from find_work.types import VersionBump
from find_work.utils import (
    aiohttp_session,
    read_json_cache,
    write_json_cache,
)


async def _fetch_outdated() -> list[dict]:
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
            data = await response.json()
    return data.get("data", {}).get("outdatedPackages", [])


def _collect_version_bumps(data: Iterable[dict],
                           options: Options) -> SortedSet[VersionBump]:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    result: SortedSet[VersionBump] = SortedSet()
    for item in data:
        bump = VersionBump(item["Atom"],
                           item.get("GentooVersion", "(unknown)"),
                           item.get("NewestVersion", "(unknown)"))

        if options.only_installed and bump.atom not in pm.installed:
            continue
        result.add(bump)
    return result


async def _outdated(options: Options) -> None:
    if options.maintainer:
        raise NotImplementedError("-m option is not implemented for this command")

    dots = ProgressDots(options.verbose)

    options.say(Message.CACHE_LOAD)
    with dots():
        data = read_json_cache(options.cache_key)
    if data is None:
        options.vecho("Fetching data from Gentoo Packages API",
                      nl=False, err=True)
        with dots():
            data = await _fetch_outdated()
        if len(data) == 0:
            options.say(Message.EMPTY_RESPONSE)
            return
        options.say(Message.CACHE_WRITE)
        with dots():
            write_json_cache(data, options.cache_key)

    outdated_set = _collect_version_bumps(data, options)
    for bump in outdated_set:
        options.echo(bump.atom + " ", nl=False)
        options.secho(bump.old_version, fg="red", nl=False)
        options.echo(" → ", nl=False)
        options.secho(bump.new_version, fg="green")

    if len(outdated_set) == 0:
        options.say(Message.NO_WORK)


async def _fetch_maintainer_stabilization(maintainer: str) -> list[dict]:
    url = f"{PGO_BASE_URL}/maintainer/{maintainer}/stabilization.json"
    async with aiohttp_session() as session:
        async with session.get(url, raise_for_status=True) as response:
            data = await response.json()

    # bring data to a common structure
    return [
        {
            "Atom": f"{item['category']}/{item['package']}",
            "Version": item["version"],
            "Message": item["message"],
        }
        for item in data
    ]


async def _fetch_all_stabilization() -> list[dict]:
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
            data = await response.json()
    return data.get("data", {}).get("pkgCheckResults", [])


async def _fetch_stabilization(options: Options) -> list[dict]:
    if options.maintainer:
        return await _fetch_maintainer_stabilization(options.maintainer)
    return await _fetch_all_stabilization()


def _collect_stable_candidates(data: list[dict],
                               options: Options) -> SortedDict[str, str]:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    result: SortedDict[str, str] = SortedDict()
    for item in data:
        if options.only_installed and item["Atom"] not in pm.installed:
            continue
        key = "-".join([item["Atom"], item["Version"]])
        result[key] = item["Message"]
    return result


async def _stabilization(options: Options) -> None:
    dots = ProgressDots(options.verbose)

    options.say(Message.CACHE_LOAD)
    with dots():
        data = read_json_cache(options.cache_key)
    if data is None:
        options.vecho("Fetching data from Gentoo Packages API",
                      nl=False, err=True)
        with dots():
            data = await _fetch_stabilization(options)
        if len(data) == 0:
            options.say(Message.EMPTY_RESPONSE)
            return
        options.say(Message.CACHE_WRITE)
        with dots():
            write_json_cache(data, options.cache_key)

    candidates = _collect_stable_candidates(data, options)
    if len(candidates) != 0:
        options.echo(tabulate(candidates.items(), tablefmt="plain"))
    else:
        options.say(Message.NO_WORK)


@click.command()
@click.pass_obj
def outdated(options: Options) -> None:
    """ Find outdated packages. """
    options.cache_key.feed("outdated")
    asyncio.run(_outdated(options))


@click.command()
@click.pass_obj
def stabilization(options: Options) -> None:
    """ Find outdated packages. """
    options.cache_key.feed("stabilization")
    asyncio.run(_stabilization(options))
