# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Utility functions and classes. """

import hashlib
import json
import tempfile
import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiohttp

from find_work.constants import PACKAGE, USER_AGENT
from find_work.types import CacheKey

with warnings.catch_warnings():
    # Disable annoying warning shown to LibreSSL users
    warnings.simplefilter("ignore")
    import requests


@asynccontextmanager
async def aiohttp_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """
    Construct an :py:class:`aiohttp.ClientSession` object with out settings.
    """

    headers = {"user-agent": USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=30)
    session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    try:
        yield session
    finally:
        await session.close()


def requests_session() -> requests.Session:
    """
    Construct an :py:class:`requests.Session` object with out settings.
    """
    session = requests.Session()
    session.headers["user-agent"] = USER_AGENT
    return session


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
    :returns: decoded data or ``None``
    """

    cache = _get_cache_path(bytes(cache_key))
    if not cache.is_file():
        return None

    with open(cache) as file:
        return json.load(file, **kwargs)
