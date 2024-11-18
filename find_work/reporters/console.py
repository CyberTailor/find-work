# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Results reporter for the console.
"""

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


class TabulateConsoleReporter(AbstractReporter[T]):
    """
    Console reporter using the Tabulate library.
    """

    reporter_name = "console"
    _items: list[T]

    def __enter__(self) -> "TabulateConsoleReporter":
        self._items = []

        return self

    @property
    def active(self) -> bool:
        return _HAS_TABULATE


class ConsoleVersionBumpReporter(AbstractReporter[VersionBump]):
    reporter_name = "console"
    result_type = VersionBump

    @validate_call
    def add_result(self, item: VersionBump) -> None:
        self.options.echo(item.atom + " ", nl=False)
        self.options.secho(item.old_version, fg="red", nl=False)
        self.options.echo(" → ", nl=False)
        self.options.secho(item.new_version, fg="green")


class ConsoleBugViewReporter(TabulateConsoleReporter[BugView]):
    result_type = BugView

    def __exit__(self, *args: Any) -> None:
        print(tabulate(self._items, tablefmt="plain"))  # type: ignore

    @validate_call
    def add_result(self, item: BugView) -> None:
        self._items.append(item)


class ConsolePkgcheckResultReporter(AbstractReporter[PkgcheckResultsGroup]):
    reporter_name = "console"
    result_type = PkgcheckResultsGroup

    def add_result(self, item: PkgcheckResultsGroup) -> None:
        self.options.echo()
        self.options.secho(item["atom"], fg="cyan", bold=True)
        for result in item["results"]:
            self.options.echo("\t", nl=False)
            self.options.secho(result.name, fg=result.priority.color, nl=False)
            self.options.echo(": ", nl=False)
            self.options.echo(result.desc)
