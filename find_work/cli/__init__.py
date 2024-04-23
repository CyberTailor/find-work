# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Basic command-line functionality. """

import threading
from abc import ABC, abstractmethod
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import field
from functools import cached_property
from enum import Enum, auto
from typing import Any

import click
from pydantic.dataclasses import dataclass

from find_work.cache import CacheKey
from find_work.config import load_config


class ProgressDots:
    """ Print a dot to the terminal every second. """

    def __init__(self, active: bool) -> None:
        self.active = active
        self._timer: threading.Timer | None = None

    def _tick(self) -> None:
        click.echo(" .", nl=False, err=True)
        self._timer = threading.Timer(1.0, self._tick)
        self._timer.start()

    def _start(self) -> None:
        if not self.active:
            return

        self._timer = threading.Timer(1.0, self._tick)
        self._timer.start()

    def _stop(self) -> None:
        if not self.active or self._timer is None:
            return

        self._timer.cancel()
        click.echo()

    @contextmanager
    def __call__(self) -> Generator[None, None, None]:
        self._start()
        try:
            yield
        finally:
            self._stop()


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


@dataclass
class BugzillaOptions(ModuleOptionsBase):
    """ Bugzilla subcommand options. """

    # Product name.
    product: str = ""

    # Component name.
    component: str = ""

    # Bug summary.
    short_desc: str = ""

    # Sort by date last modified or by ID.
    chronological_sort: bool = False

    @cached_property
    def cache_order(self) -> list[str]:
        return ["chronological_sort", "short_desc", "product", "component"]


@dataclass
class PgoOptions(ModuleOptionsBase):
    """ Gentoo Packages subcommand options. """

    @cached_property
    def cache_order(self) -> list[str]:
        return []


@dataclass
class PkgcheckOptions(ModuleOptionsBase):
    """ pkgcheck subcommand options. """

    # Repository name or absolute path.
    repo: str = ""

    # Class of the pkgcheck warning, e.g. DeprecatedEapi
    keywords: list[str] = field(default_factory=list)

    # Message of the pkgcheck warning, e.g. 'uses deprecated EAPI 5'
    message: str = ""

    @cached_property
    def cache_order(self) -> list[str]:
        return ["repo", "keywords", "message"]


@dataclass
class RepologyOptions(ModuleOptionsBase):
    """ Repology subcommand options. """

    # Repository name.
    repo: str = ""

    @cached_property
    def cache_order(self) -> list[str]:
        return ["repo"]


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

    #: Subcommand options.
    bugzilla: BugzillaOptions = field(default_factory=BugzillaOptions)
    pgo: PgoOptions = field(default_factory=PgoOptions)
    pkgcheck: PkgcheckOptions = field(default_factory=PkgcheckOptions)
    repology: RepologyOptions = field(default_factory=RepologyOptions)

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
