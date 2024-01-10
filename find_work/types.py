# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Type definitions for the application, implemented as Pydantic models. """

from dataclasses import field
from typing import Any

from pydantic.dataclasses import dataclass


@dataclass(frozen=True, order=True)
class VersionBump:
    """ Version bump representation for a Gentoo repository. """

    atom: str
    old_version: str = field(compare=False)
    new_version: str = field(compare=False)


@dataclass(frozen=True, order=True)
class BugView:
    """ Bug listing item representation. """

    bug_id: int
    last_change_date: str = field(compare=False)
    assigned_to: str = field(compare=False)
    summary: str = field(compare=False)


@dataclass
class CacheKey:
    """
    Cache key constructor.

    >>> key = CacheKey()
    >>> key.feed(b"bytes")
    >>> key.feed("string")
    >>> key.feed(count=42)
    >>> key.feed(flag=True)
    >>> bytes(key)
    b'bytes\\x00string\\x00count:42\\x00flag:1\\x00'
    >>> key.feed([1, 2, 3])
    Traceback (most recent call last):
        ...
    TypeError: Unsupported type conversion
    """

    data: bytes = b""

    @staticmethod
    def _encode(value: Any) -> bytes:
        match value:
            case bytes():
                return value
            case str():
                return value.encode()
            case bool():
                return b"1" if value else b"0"
            case int():
                return str(value).encode()
            case _:
                raise TypeError("Unsupported type conversion")

    def feed(self, *args: Any, **kwargs: Any) -> None:
        """ Update the key with new data. """
        if args and kwargs or len(kwargs) > 1:
            raise ValueError("Too many arguments")

        for value in args:
            self.data += self._encode(value) + b"\0"

        for key, value in kwargs.items():
            self.data += self._encode(key) + b":"
            self.data += self._encode(value) + b"\0"

    def __bytes__(self) -> bytes:
        return self.data
