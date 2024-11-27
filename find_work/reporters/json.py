# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Results reporter for machine-readable JSON output.
"""

from typing import Any, TypeVar

from pydantic import TypeAdapter, validate_call

from find_work.core.reporters import AbstractReporter
from find_work.core.types.results import (
    BugView,
    PkgcheckResultsGroup,
    VersionBump,
)

T = TypeVar("T")


class JsonReporter(AbstractReporter[T]):
    """
    JSON reporter using Pydantic model serialization.
    """

    reporter_name = "json"
    _items: list[T]

    def __enter__(self) -> "JsonReporter":
        self._items = []

        return self

    @validate_call
    def add_result(self, item: T) -> None:
        self._items.append(item)

    def __exit__(self, *args: Any) -> None:
        self.options.echo(
            TypeAdapter(list[T]).dump_json(
                self._items, indent=2
            ).decode()
        )


class JsonVersionBumpReporter(JsonReporter[VersionBump]):
    result_type = VersionBump

    @validate_call
    def add_result(self, item: VersionBump) -> None:
        super().add_result(item)


class JsonBugViewReporter(JsonReporter[BugView]):
    result_type = BugView

    @validate_call
    def add_result(self, item: BugView) -> None:
        super().add_result(item)


class JsonPkgcheckResultReporter(JsonReporter[PkgcheckResultsGroup]):
    result_type = PkgcheckResultsGroup

    @validate_call
    def add_result(self, item: PkgcheckResultsGroup) -> None:
        super().add_result(item)
