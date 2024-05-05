# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Command line options implemented as a single object.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

import click
from pydantic import BaseModel, ConfigDict, Field

from find_work.cli import colors_disabled_by_env
from find_work.types.breadcrumbs import Breadcrumbs


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

    #: Display only packages for given maintainer email.
    maintainer: str = ""

    #: Display installed packages only.
    only_installed: bool = False

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

    @staticmethod
    def echo(message: Any | None = None, **kwargs: Any) -> None:
        """
        Simple alias to :py:function:`click.echo`.
        """

        click.echo(message, **kwargs)

    def vecho(self, message: Any | None = None, **kwargs: Any) -> None:
        """
        Alias to :py:function:`click.echo` but with our verbosity settings.
        """

        if self.verbose:
            click.echo(message, **kwargs)

    def secho(self, message: Any | None = None, **kwargs: Any) -> None:
        """
        Alias to :py:function:`click.secho` but with our color settings.
        """

        kwargs.pop("color", None)
        if self.colors is None and colors_disabled_by_env():
            self.colors = False

        click.secho(message, color=self.colors, **kwargs)

    @property
    def attr_order(self) -> Sequence[str]:
        return tuple()
