# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
CLI subcommands for everything Bugzilla.
"""

import warnings
from collections.abc import Collection
from datetime import datetime
from typing import Any

import click
import gentoopm
import pydantic_core
from tabulate import tabulate

from find_work.cache import (
    read_raw_json_cache,
    write_raw_json_cache,
)
from find_work.cli import Message, Options, ProgressDots
from find_work.constants import BUGZILLA_URL
from find_work.types import BugView
from find_work.utils import (
    extract_package_name,
    requests_session,
)

with warnings.catch_warnings():
    # Disable annoying warning shown to LibreSSL users
    warnings.simplefilter("ignore")
    import bugzilla
    from bugzilla.bug import Bug


def _bugs_from_raw_json(raw_json: str | bytes) -> list[Bug]:
    data: list[dict] = pydantic_core.from_json(raw_json)
    with requests_session() as session:
        bz = bugzilla.Bugzilla(BUGZILLA_URL, requests_session=session,
                               force_rest=True)
        return [Bug(bz, dict=bug) for bug in data]


def _bugs_to_raw_json(data: Collection[Bug]) -> bytes:
    raw_data = [bug.get_raw_data() for bug in data]
    return pydantic_core.to_json(raw_data, exclude_none=True)


def _fetch_bugs(options: Options, **kwargs: Any) -> list[Bug]:
    with requests_session() as session:
        bz = bugzilla.Bugzilla(BUGZILLA_URL, requests_session=session,
                               force_rest=True)
        query = bz.build_query(
            short_desc=options.bugzilla.short_desc or None,
            product=options.bugzilla.product or None,
            component=options.bugzilla.component or None,
            assigned_to=options.maintainer or None,
        )
        query["resolution"] = "---"
        if options.bugzilla.chronological_sort:
            query["order"] = "changeddate DESC"
        else:
            query["order"] = "bug_id DESC"
        return bz.query(query)


def _collect_bugs(data: Collection[Bug], options: Options) -> list[BugView]:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    result: list[BugView] = []
    for bug in data:
        if options.only_installed:
            if (package := extract_package_name(bug.summary)) is None:
                continue
            if package not in pm.installed:
                continue

        date = datetime.fromisoformat(bug.last_change_time).date().isoformat()
        item = BugView(bug.id, date, bug.assigned_to, bug.summary)
        result.append(item)
    return result


def _list_bugs(cmd: str, options: Options, **filters: Any) -> None:
    options.cache_key.feed(cmd)
    dots = ProgressDots(options.verbose)

    options.say(Message.CACHE_LOAD)
    with dots():
        raw_data = read_raw_json_cache(options.cache_key)
    if raw_data:
        options.say(Message.CACHE_READ)
        with dots():
            data = _bugs_from_raw_json(raw_data)
    else:
        options.vecho("Fetching data from Bugzilla API", nl=False, err=True)
        with dots():
            data = _fetch_bugs(options, **filters)
        if len(data) == 0:
            options.say(Message.EMPTY_RESPONSE)
            return
        options.say(Message.CACHE_WRITE)
        with dots():
            raw_json = _bugs_to_raw_json(data)
            write_raw_json_cache(raw_json, options.cache_key)

    bumps = _collect_bugs(data, options)
    if len(bumps) != 0:
        options.echo(tabulate(bumps, tablefmt="plain"))  # type: ignore
    else:
        options.say(Message.NO_WORK)


@click.command("list")
@click.pass_obj
def ls(options: Options) -> None:
    """ List bugs on Bugzilla. """
    _list_bugs("list", options)
