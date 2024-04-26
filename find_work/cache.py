# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Implementation of caching functionality. """

import hashlib
import tempfile
from pathlib import Path
from typing import Any, SupportsBytes

from pydantic import BaseModel, PrivateAttr

from find_work.constants import PACKAGE


class CacheKey(BaseModel):
    """
    Cache key constructor.

    >>> key = CacheKey()
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
    >>> key.feed_option("keywords", ["wow", "amazing"])
    True
    >>> bytes(key)
    b'bytes\\x00string\\x00count:42\\x00flag:1\\x00keywords:amazing\\x19wow\\x00'
    >>> key.feed({1, 2, 3})
    Traceback (most recent call last):
        ...
    TypeError: Unsupported type: set
    """

    _data: bytes = PrivateAttr(default=b"")

    @staticmethod
    def _unsupported_type(value: Any) -> TypeError:
        return TypeError(f"Unsupported type: {type(value).__name__}")

    @classmethod
    def _encode(cls, value: Any) -> bytes:
        match value:
            case bytes():
                return value
            case str():
                return value.encode()
            case list():
                return b"\31".join(map(cls._encode, sorted(value)))
            case bool():
                return b"1" if value else b"0"
            case int():
                return str(value).encode()
            case _:
                raise cls._unsupported_type(value)

    @classmethod
    def _feedable(cls, value: Any) -> bool:
        match value:
            case bytes() | str() | list():
                return bool(value)
            case bool() | int():
                return True
            case None:
                return False
            case _:
                raise cls._unsupported_type(value)

    def feed(self, *args: Any) -> bool:
        """
        Update the key with new data.

        :return: ``True`` if data was accepted, ``False`` otherwise
        """

        accepted: bool = False
        for value in filter(self._feedable, args):
            self._data += self._encode(value) + b"\0"
            accepted = True
        return accepted

    def feed_option(self, key: str, value: Any) -> bool:
        """
        Update the key with new key-value data.

        :return: ``True`` if data was accepted, ``False`` otherwise
        """

        if self._feedable(value):
            self._data += self._encode(key) + b":"
            self._data += self._encode(value) + b"\0"
            return True
        return False

    def __bytes__(self) -> bytes:
        return self._data


def _get_cache_path(cache_key: SupportsBytes) -> Path:
    hexdigest = hashlib.sha256(bytes(cache_key)).hexdigest()
    file = Path(tempfile.gettempdir()) / PACKAGE / hexdigest
    return file.with_suffix(".json")


def write_raw_json_cache(data: SupportsBytes, cache_key: SupportsBytes) -> None:
    """
    Write a JSON cache file in a temporary directory.

    This function silently fails on OS errors.

    :param data: raw JSON
    :param cache_key: cache key object
    """

    cache = _get_cache_path(cache_key)
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return

    with open(cache, "wb") as file:
        try:
            file.write(bytes(data))
        except OSError:
            pass


def read_raw_json_cache(cache_key: SupportsBytes) -> bytes:
    """
    Read a JSON cache file stored in a temporary directory.

    :param cache_key: cache key object

    :return: raw JSON file contents or empty byte string
    """

    cache = _get_cache_path(cache_key)
    if not cache.is_file():
        return b""

    with open(cache, "rb") as file:
        return file.read()
