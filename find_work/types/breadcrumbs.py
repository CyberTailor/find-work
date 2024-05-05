# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Construct a breadcrumb trail.
"""

import hashlib
from collections.abc import Collection
from typing import Any

from pydantic import BaseModel, PrivateAttr


class Breadcrumbs(BaseModel):
    """
    Construct a predictable key in a chain-like manner.

    The following primitives are stored:

    - Booleans

    - Integer numbers

    - Non-empty strings and bytestrings

    - Non-empty collections (lists, sets) of everything above

    The following primitives are ignored:

    - The ``None`` object

    - Empty string and bytestrings

    - Empty collections

    Everything other raises :py:class:`TypeError`.

    >>> key = Breadcrumbs()
    >>> key.feed(b"bytes")
    True
    >>> key.feed("string")
    True
    >>> key.feed("")
    False
    >>> key.feed_option("count", 42)
    True
    >>> key.feed_option("flag", True)
    True
    >>> key.feed_option("keywords", {"wow", "amazing"})
    True
    >>> bytes(key)
    b'bytes\\x00string\\x00count:42\\x00flag:1\\x00keywords:amazing\\x19wow\\x00'
    >>> key.hexdigest()
    '45c1f10e9d639892a42c7755e59c3dc8eb5d33b83dd2fe4531e99f02a682c233'
    """

    _data: bytes = PrivateAttr(default=b"")

    def __bytes__(self) -> bytes:
        return self._data

    def hexdigest(self) -> str:
        """
        Hash the data with SHA-256 and return its hexadecimal digest.
        """

        return hashlib.sha256(self._data).hexdigest()

    def feed(self, *args: Any) -> bool:
        """
        Update the key with new data.

        This operation is irreversible.

        :raises TypeError: on unsupported types

        :return: whether data was accepted
        """

        accepted: bool = False
        for value in filter(self._feedable, args):
            self._data += self._encode(value) + b"\0"
            accepted = True
        return accepted

    def feed_option(self, key: str, value: Any) -> bool:
        """
        Update the key with new key-value data.

        This operation is irreversible.

        :raises TypeError: on unsupported types

        :return: whether data was accepted
        """

        if self._feedable(value):
            self._data += self._encode(key) + b":"
            self._data += self._encode(value) + b"\0"
            return True
        return False

    @staticmethod
    def _unsupported_type(value: Any) -> TypeError:
        return TypeError(f"Unsupported type: {type(value).__name__}")

    def _encode(self, value: Any) -> bytes:
        match value:
            case bytes() | bytearray():
                return value
            case str():
                return value.encode()
            case bool():
                return b"1" if value else b"0"
            case int():
                return str(value).encode()
            case Collection():
                return b"\31".join(map(self._encode, sorted(value)))
            case _:
                raise self._unsupported_type(value)

    def _feedable(self, value: Any) -> bool:
        match value:
            case Collection() | bytes() | bytearray() | str():
                return len(value) != 0
            case bool() | int():
                return True
            case None:
                return False
            case _:
                raise self._unsupported_type(value)
