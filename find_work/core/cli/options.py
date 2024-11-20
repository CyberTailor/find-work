# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Command line options implemented as a single object.
"""

import importlib.metadata
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, TYPE_CHECKING

import click
from pydantic import BaseModel, ConfigDict, Field, validate_call

from find_work.core.cli.messages import Result
from find_work.core.constants import REPORTERS_ENTRY_POINT
from find_work.core.types.breadcrumbs import Breadcrumbs

if TYPE_CHECKING:
    # Circular import.
    from find_work.core.reporters import AbstractReporter


class OptionsBase(BaseModel, ABC):
    """
    Base class for all option objects.
    """
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    #: Subcommand options.
    children: dict[str, "OptionsBase"] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    @property
    @abstractmethod
    def attr_order(self) -> Sequence[str]:
        """
        Sequence of attributes, in order they'll appear in breadcrumbs.
        """


class MainOptions(OptionsBase):
    """
    Main application options.
    """

    #: Enable/disable colors.
    colors: bool | None = None

    #: Enable/disable progress reporting.
    verbose: bool = True

    #: Unique predictable identificator that can be used as a cache key.
    breadcrumbs: Breadcrumbs = Field(default_factory=Breadcrumbs)

    #: Select a reporter to use for output.
    reporter_name: str = ""

    #: Display only packages for given maintainer email.
    maintainer: str = ""

    #: Display installed packages only.
    only_installed: bool = False

    @validate_call
    def override(self, opt_module: str, opt_name: str, value: Any) -> None:
        """
        Override an option in one of the children.

        :param opt_module: "path" to the :py:class:`OptionsBase` object
        :param opt_name: target option name
        :param value: new value
        """

        target: OptionsBase = self
        for opt_group in filter(None, opt_module.split(".")):
            target = target.children[opt_group]
        target[opt_name] = value

    def get_reporter_for(self, result_type: type) -> "AbstractReporter":
        """
        Get a reporter to output results.

        :param result_type: result type (class) to represent

        :returns: reporter instance to use in a context manager
        :raises RuntimeError: when no suitable reporters found
        """

        from find_work.core.reporters import AbstractReporter

        for ep in importlib.metadata.entry_points(group=REPORTERS_ENTRY_POINT):
            cls = ep.load()
            if (
                isinstance(cls, type)
                and issubclass(cls, AbstractReporter)
                and cls.reporter_name == self.reporter_name
                and cls.result_type is result_type
                and (result := cls(self)).active
            ):
                return result

        raise RuntimeError(f"No reporters found to represent {result_type} "
                           f"with '{self.reporter_name}' reporter")

    @staticmethod
    def echo(message: Any | None = None, **kwargs: Any) -> None:
        """
        Simple alias to :py:func:`click.echo`.
        """

        click.echo(message, **kwargs)

    def vecho(self, message: Any | None = None, **kwargs: Any) -> None:
        """
        Alias to :py:func:`click.echo` but with our verbosity settings.
        """

        if self.verbose:
            click.echo(message, **kwargs)

    def secho(self, message: Any | None = None, **kwargs: Any) -> None:
        """
        Alias to :py:func:`click.secho` but with our color settings.
        """

        kwargs.pop("color", None)
        click.secho(message, color=self.colors, **kwargs)

    def exit(self, result: Result) -> None:
        """
        Display a result message to stderr.

        :param result: result message
        """

        self.secho(result.text, fg=result.color, err=True)

    @property
    def attr_order(self) -> Sequence[str]:
        return tuple()
