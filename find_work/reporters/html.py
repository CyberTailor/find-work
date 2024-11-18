# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Results reporter for the web.
"""

import html
from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import validate_call

from find_work.core.reporters import AbstractReporter
from find_work.core.types.results import (
    BugView,
    PkgcheckResultsGroup,
    VersionBump,
)

try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ModuleNotFoundError:
    _HAS_TABULATE = False

T = TypeVar("T")


class HtmlReporter(AbstractReporter[T]):
    """
    HTML reporter using the Tabulate library.
    """

    reporter_name = "html"
    _items: list[T]

    def __enter__(self) -> "HtmlReporter":
        self._items = []

        return self

    @property
    def active(self) -> bool:
        return _HAS_TABULATE


class HtmlVersionBumpReporter(HtmlReporter[VersionBump]):
    result_type = VersionBump

    def __exit__(self, *args: Any) -> None:
        headers: list[str] = [
            "Package name",
            "Repository version",
            "Newest version",
        ]
        self.options.echo(tabulate(self._items, headers,  # type: ignore
                          tablefmt="html", disable_numparse=True))

    @validate_call
    def add_result(self, item: VersionBump) -> None:
        self._items.append(item)


class HtmlBugViewReporter(HtmlReporter[BugView]):
    result_type = BugView

    def __exit__(self, *args: Any) -> None:
        headers: list[str] = [
            "ID",
            "Changed",
            "Assignee",
            "Summary",
        ]
        self.options.echo(tabulate(self._items, headers,  # type: ignore
                                   tablefmt="html"))

    @validate_call
    def add_result(self, item: BugView) -> None:
        self._items.append(item)


class HtmlPkgcheckResultReporter(AbstractReporter[PkgcheckResultsGroup]):
    reporter_name = "html"
    result_type = PkgcheckResultsGroup

    _headers: Sequence[str] = (
        "Level",
        "Class",
        "Description",
    )

    def add_result(self, item: PkgcheckResultsGroup) -> None:
        self.options.echo("<h2>{}</h2>".format(html.escape(item["atom"])))
        self.options.echo(tabulate(item["results"], self._headers,  # type: ignore
                                   tablefmt="html"))

    @property
    def active(self) -> bool:
        return _HAS_TABULATE
