# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Result reporters to use for output.
"""

from abc import abstractmethod
from contextlib import AbstractContextManager
from typing import Any, Generic, TypeVar

from find_work.core.cli.options import MainOptions

T = TypeVar("T")


class AbstractReporter(AbstractContextManager, Generic[T]):
    """
    Generic class for result reporters.
    """

    #: Name to identify the reporter.
    reporter_name: str

    #: Result type (class) supported by this reporter.
    result_type: type

    def __init__(self, options: MainOptions):
        """
        :param options: main application options
        """

        self.options = options

    def __exit__(self, *args: Any) -> None:
        return None

    @abstractmethod
    def add_result(self, item: T) -> None:
        """
        Format and print a single item to the standard output.

        :param item: an instance of one of the supported result types
        """

    @property
    def active(self) -> bool:
        """
        Whether all dependencies of the reporter are met.
        """

        return True
