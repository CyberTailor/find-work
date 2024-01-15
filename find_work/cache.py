# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Implementation of caching functionality. """

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from pydantic.dataclasses import dataclass

from find_work.constants import PACKAGE


@dataclass
class CacheKey:
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

    data: bytes = b""

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
            self.data += self._encode(value) + b"\0"
            accepted = True
        return accepted

    def feed_option(self, key: str, value: Any) -> bool:
        """
        Update the key with new key-value data.

        :return: ``True`` if data was accepted, ``False`` otherwise
        """

        if self._feedable(value):
            self.data += self._encode(key) + b":"
            self.data += self._encode(value) + b"\0"
            return True
        return False

    def __bytes__(self) -> bytes:
        return self.data


def _get_cache_path(cache_key: bytes) -> Path:
    hexdigest = hashlib.sha256(cache_key).hexdigest()
    file = Path(tempfile.gettempdir()) / PACKAGE / hexdigest
    return file.with_suffix(".json")


def write_json_cache(data: Any, cache_key: CacheKey, **kwargs: Any) -> None:
    """
    Write a JSON cache file in a temporary directory. Keyword arguments are
    passed to :py:function:`json.dump` as is.

    :param data: data to serialize
    :param cache_key: cache key object
    """

    cache = _get_cache_path(bytes(cache_key))
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return

    with open(cache, "w") as file:
        try:
            json.dump(data, file, **kwargs)
        except OSError:
            pass


def read_json_cache(cache_key: CacheKey, **kwargs: Any) -> Any | None:
    """
    Read a JSON cache file stored in a temporary directory. Keyword arguments
    are passed to :py:function:`json.load` as is.

    :param cache_key: cache key object
    :return: decoded data or ``None``
    """

    cache = _get_cache_path(bytes(cache_key))
    if not cache.is_file():
        return None

    with open(cache) as file:
        return json.load(file, **kwargs)
