# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Components for displaying imformation to the console.
"""

import threading
from collections.abc import Generator
from contextlib import contextmanager

import click


class ProgressDots:
    """
    Print a status indicator to the terminal at equal intervals of time::

        import sys
        import time

        dots = ProgressDots(sys.stderr.isatty())
        with dots("Doing stuff"):
            time.sleep(5.5)

    The example above would print::

        Doing stuff . . . . .

    Implementation notes:

    - First indication is delayed by the interval length.

    - When the indication stops, a newline is printed.
    """

    interval: float = 2.0
    indicator: str = " ."

    def __init__(self, enabled: bool):
        """
        :param enabled: whether to actually print anything
        """

        self.enabled = enabled

        self._timer: threading.Timer | None = None

    def _tick(self) -> None:
        click.echo(self.indicator, nl=False, err=True)
        self._setup_timer()

    def _teardown_timer(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _setup_timer(self) -> None:
        self._teardown_timer()

        self._timer = threading.Timer(self.interval, self._tick)
        self._timer.start()

    @contextmanager
    def __call__(self, message: str = "") -> Generator[None, None, None]:
        """
        Make a context manager.

        :param message: status message that will be printed once
        """

        if not self.enabled:
            yield
            return

        click.echo(message, nl=False, err=True)
        self._setup_timer()
        try:
            yield
        finally:
            self._teardown_timer()
            click.echo(err=True)
