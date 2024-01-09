# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Modules implementing command-line functionality. """

import threading
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import field
from typing import Any

import click

from pydantic.dataclasses import dataclass


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

    # Repository name
    repo: str = ""


@dataclass
class Options:
    """ Global options. """

    # Enable/disable colors.
    colors: bool | None = None

    # Enable/disable progress reporting.
    verbose: bool = True

    # Filter installed packages only
    only_installed: bool = False

    # String used for creating cache key
    cache_key: bytes = b""

    # Repology subcommand options
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
