# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Basic command-line functionality. """

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import field
from enum import Enum, auto
from typing import Any

import click
from pydantic.dataclasses import dataclass

from find_work.cache import CacheKey
from find_work.config import load_config


class OptionsBase(ABC):
    """ Base class for all options. """

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)


class ModuleOptionsBase(OptionsBase, ABC):
    """ Base class for module-specific options. """

    #: Extra options used in the command scope.
    extra_options: dict[str, Any] | None = None

    @property
    @abstractmethod
    def cache_order(self) -> list[str]:
        ...


class Message(Enum):
    """ Typical messages. """

    CACHE_READ = auto()
    CACHE_LOAD = auto()
    CACHE_WRITE = auto()

    EMPTY_RESPONSE = auto()
    NO_WORK = auto()


@dataclass
class Options(OptionsBase):
    """ Global options. """

    # Enable/disable colors.
    colors: bool | None = None

    # Maintainer email.
    maintainer: str = ""

    # Enable/disable progress reporting.
    verbose: bool = True

    # Filter installed packages only
    only_installed: bool = False

    # Byte string used for creating cache key.
    cache_key: CacheKey = field(default_factory=CacheKey)

    @staticmethod
    def echo(*args: Any, **kwargs: Any) -> None:
        """
        Simple alias to :py:function:`click.echo`.
        """

        click.echo(*args, **kwargs)

    def vecho(self, *args: Any, **kwargs: Any) -> None:
        """
        Alias to :py:function:`click.echo` but with our verbosity settings.
        """

        if self.verbose:
            click.echo(*args, **kwargs)

    def secho(self, *args: Any, **kwargs: Any) -> None:
        """
        Alias to :py:function:`click.secho` but with our color settings.
        """

        kwargs.pop("color", None)
        click.secho(*args, color=self.colors, **kwargs)  # type: ignore

    def say(self, msgid: Message) -> None:
        """
        Output one of pre-configured messages to the terminal.

        :param msgid: message type
        """

        match msgid:
            case Message.CACHE_LOAD:
                self.vecho("Checking for cached data", nl=False, err=True)
            case Message.CACHE_READ:
                self.vecho("Reading cached data", nl=False, err=True)
            case Message.CACHE_WRITE:
                self.vecho("Caching data", nl=False, err=True)
            case Message.EMPTY_RESPONSE:
                self.secho("Hmmm, no data returned. Try again with different "
                           "arguments.", fg="yellow")
            case Message.NO_WORK:
                self.secho("Congrats! You have nothing to do!", fg="green")
            case _:
                raise TypeError(f"Unknown message identifier: {msgid}")


def apply_custom_flags(callback: Callable) -> Callable:
    """
    A decorator function to load custom global flags from configuration files.
    """

    for flag in load_config().flags:
        names = [f"--{flag.name}"]
        names += flag.shortcuts
        callback = click.option(*names, help=flag.description, is_flag=True)(callback)
    return callback
