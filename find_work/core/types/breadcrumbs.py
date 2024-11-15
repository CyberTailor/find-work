# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Construct a breadcrumb trail.
"""

import hashlib
from collections.abc import Collection, Sized
from typing import assert_never, cast

from pydantic import (
    BaseModel,
    PrivateAttr,
    StrictBool,
    StrictBytes,
    StrictInt,
    StrictStr,
    validate_call,
)

BasicTypes = StrictBool | StrictBytes | StrictInt | StrictStr
SupportedValue = BasicTypes | tuple[BasicTypes | None, ...]


@validate_call
def is_feedable(value: SupportedValue | None) -> bool:
    match value:
        case tuple():
            return any(is_feedable(element) for element in value)
        case Sized():
            return len(value) != 0
        case bool() | int():
            return True
        case None:
            return False
        case _:
            assert_never(value)


@validate_call
def encode_value(value: SupportedValue) -> bytes:
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
            return b"\31".join(
                sorted(encode_value(cast(BasicTypes, element))
                       for element in value
                       if is_feedable(element))
            )
        case _:
            assert_never(value)


class Breadcrumbs(BaseModel):
    """
    Construct a predictable key in a chain-like manner.

    The following primitives are stored:

    - Booleans

    - Integer numbers

    - Non-empty strings and bytestrings

    - ``list``, ``tuple``, ``set``, ``frozenset``, ``deque`` and generators of
      everything above

    The following primitives are ignored:

    - The ``None`` object

    - Empty string and bytestrings

    - Empty collections

    Everything other raises error.

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

    @validate_call
    def feed(self, *args: SupportedValue | None) -> bool:
        """
        Update the key with new data.

        This operation is irreversible.

        :return: whether data was accepted
        """

        accepted: bool = False
        for value in filter(is_feedable, args):
            self._data += encode_value(cast(SupportedValue, value)) + b"\0"
            accepted = True
        return accepted

    @validate_call
    def feed_option(self, key: str, value: SupportedValue | None) -> bool:
        """
        Update the key with new key-value data.

        This operation is irreversible.

        :return: whether data was accepted
        """

        if is_feedable(key) and is_feedable(value):
            self._data += encode_value(key) + b":"
            self._data += encode_value(cast(SupportedValue, value)) + b"\0"
            return True
        return False


__all__ = [
    "Breadcrumbs"
]
