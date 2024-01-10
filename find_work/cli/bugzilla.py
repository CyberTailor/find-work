# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
CLI subcommands for everything Bugzilla.

This Python module also defines some regular expressions.

``pkg_re`` matches package name and version from bug summaries:

>>> ant_match = pkg_re.search(">=dev-java/ant-1.10.14: version bump - needed for jdk:21")
>>> (ant_match.group("package"), ant_match.group("version"))
('dev-java/ant', '1.10.14')
>>> libjxl_match = pkg_re.search("media-libs/libjxl: version bump")
>>> (libjxl_match.group("package"), libjxl_match.group("version"))
('media-libs/libjxl', None)
>>> tricky_match = pkg_re.search("app-foo/bar-2-baz-4.0: version bump")
>>> (tricky_match.group("package"), tricky_match.group("version"))
('app-foo/bar-2-baz', '4.0')
>>> pkg_re.search("Please bump Firefox") is None
True

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

from find_work.cli import Message, Options, ProgressDots
from find_work.constants import BUGZILLA_URL
from find_work.types import BugView
from find_work.utils import (
    requests_session,
    read_json_cache,
    write_json_cache,
)

with warnings.catch_warnings():
    # Disable annoying warning shown to LibreSSL users
    warnings.simplefilter("ignore")
    import bugzilla
    from bugzilla.bug import Bug

# `category/package` matching according to PMS, and arbitrary version
pkg_re = re.compile(r"""(?P<package>
                            [\w][-+.\w]*    # category
                            /               # single slash
                            [\w][+\w]*      # package name before first '-'
                            (-[+\w]*(?=-))* # rest of package name
                        )
                        (
                            -               # single hyphen
                            (?P<version>
                                \d+[.\w]*   # arbitrary version
                            )
                        )?""",
                    re.VERBOSE)

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


def _fetch_bump_requests(options: Options) -> list[Bug]:
    with requests_session() as session:
        bz = bugzilla.Bugzilla(BUGZILLA_URL, requests_session=session)
        query = bz.build_query(
            product=options.bugzilla.product or None,
            component=options.bugzilla.component or None,
            assigned_to=options.maintainer or None,
            short_desc="version bump",
        )
        query["resolution"] = "---"
        if options.bugzilla.chronological_sort:
            query["order"] = "changeddate DESC"
        else:
            query["order"] = "bug_id DESC"
        return bz.query(query)


def _collect_bump_requests(data: Iterable[Bug],
                           options: Options) -> list[BugView]:
    if options.only_installed:
        pm = gentoopm.get_package_manager()

    result: list[BugView] = []
    for bug in data:
        if options.only_installed:
            if (match := pkg_re.search(bug.summary)) is None:
                continue
            if match.group("package") not in pm.installed:
                continue

        date = time.strftime("%F", bug.last_change_time.timetuple())
        item = BugView(bug.id, date, bug.assigned_to, bug.summary)
        result.append(item)
    return result


@click.command()
@click.pass_obj
def outdated(options: Options) -> None:
    """ Find packages with version bump requests on Bugzilla. """
    options.cache_key.feed("outdated")
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
            data = _fetch_bump_requests(options)
        if len(data) == 0:
            options.say(Message.EMPTY_RESPONSE)
            return
        options.say(Message.CACHE_WRITE)
        with dots():
            json_data = _bugs_to_json(data)
            write_json_cache(json_data, options.cache_key, cls=BugEncoder)

    bumps = _collect_bump_requests(data, options)
    if len(bumps) != 0:
        options.echo(tabulate(bumps, tablefmt="plain"))  # type: ignore
    else:
        options.say(Message.NO_WORK)
