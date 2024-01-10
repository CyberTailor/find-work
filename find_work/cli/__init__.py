# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Modules implementing command-line functionality. """

import threading
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import field
from enum import Enum, auto
from typing import Any

import click
from pydantic.dataclasses import dataclass

from find_work.types import CacheKey


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


@dataclass
class RepologyOptions:
    """ Repology subcommand options. """

    # Repository name.
    repo: str = ""


@dataclass
class BugzillaOptions:
    """ Bugzilla subcommand options. """

    # Product name.
    product: str = ""

    # Component name.
    component: str = ""

    # Sort by date last modified or by ID.
    chronological_sort: bool = False


class Message(Enum):
    """ Typical messages. """
    CACHE_READ = auto()
    CACHE_LOAD = auto()
    CACHE_WRITE = auto()

    EMPTY_RESPONSE = auto()
    NO_WORK = auto()


@dataclass
class Options:
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

    # Subcommand options.
    repology: RepologyOptions = field(default_factory=RepologyOptions)
    bugzilla: BugzillaOptions = field(default_factory=BugzillaOptions)

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
