# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
CLI subcommands for everything Bugzilla.

This Python module also defines some regular expressions.

``isodate_re`` matches ISO 8601 time/date strings:

>>> isodate_re.fullmatch("2024") is None
True
>>> isodate_re.fullmatch("20090916T09:04:18") is None
False
"""

import json
import re
import time
import warnings
from collections.abc import Iterable
from typing import Any
from xmlrpc.client import DateTime

import click
import gentoopm
from tabulate import tabulate

from find_work.cache import (
    read_json_cache,
    write_json_cache,
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

isodate_re = re.compile(r"\d{4}\d{2}\d{2}T\d{2}:\d{2}:\d{2}")


class BugEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, DateTime):
            return o.value
        return json.JSONEncoder.default(self, o)


def as_datetime(obj: dict) -> dict:
    result: dict = {}
    for key, value in obj.items():
        # FIXME: every matching string will be converted to DateTime
        if isinstance(value, str) and isodate_re.fullmatch(value):
            result[key] = DateTime(value)
            continue
        result[key] = value
    return result


def _bugs_from_json(data: list[dict]) -> list[Bug]:
    with requests_session() as session:
        bz = bugzilla.Bugzilla(BUGZILLA_URL, requests_session=session)
        return [Bug(bz, dict=bug) for bug in data]


def _bugs_to_json(data: Iterable[Bug]) -> list[dict]:
    return [bug.get_raw_data() for bug in data]


def _fetch_bugs(options: Options, **kwargs: Any) -> list[Bug]:
    with requests_session() as session:
        bz = bugzilla.Bugzilla(BUGZILLA_URL, requests_session=session)
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


def _collect_bugs(data: Iterable[Bug], options: Options) -> list[BugView]:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    result: list[BugView] = []
    for bug in data:
        if options.only_installed:
            if (package := extract_package_name(bug.summary)) is None:
                continue
            if package not in pm.installed:
                continue

        date = time.strftime("%F", bug.last_change_time.timetuple())
        item = BugView(bug.id, date, bug.assigned_to, bug.summary)
        result.append(item)
    return result


def _list_bugs(cmd: str, options: Options, **filters: Any) -> None:
    options.cache_key.feed(cmd)
    dots = ProgressDots(options.verbose)

    options.say(Message.CACHE_LOAD)
    with dots():
        cached_data = read_json_cache(options.cache_key,
                                      object_hook=as_datetime)
    if cached_data is not None:
        options.say(Message.CACHE_READ)
        with dots():
            data = _bugs_from_json(cached_data)
    else:
        options.vecho("Fetching data from Bugzilla API", nl=False, err=True)
        with dots():
            data = _fetch_bugs(options, **filters)
        if len(data) == 0:
            options.say(Message.EMPTY_RESPONSE)
            return
        options.say(Message.CACHE_WRITE)
        with dots():
            json_data = _bugs_to_json(data)
            write_json_cache(json_data, options.cache_key, cls=BugEncoder)

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
