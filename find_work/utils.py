# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Utility functions and classes. """

import hashlib
import json
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiohttp

from find_work.constants import PACKAGE, USER_AGENT


@asynccontextmanager
async def aiohttp_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """
    Construct an :py:class:`aiohttp.ClientSession` object.
    """

    headers = {"user-agent": USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=30)
    session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    try:
        yield session
    finally:
        await session.close()


def _get_cache_path(cache_key: bytes) -> Path:
    hexdigest = hashlib.sha256(cache_key).hexdigest()
    file = Path(tempfile.gettempdir()) / PACKAGE / hexdigest
    return file.with_suffix(".json")


def write_json_cache(data: Any, cache_key: bytes) -> None:
    """
    Write a JSON cache file in a temporary directory.

    :param data: data to serialize
    :param cache_key: hash object to use as a key
    """

    cache = _get_cache_path(cache_key)
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return

    with open(cache, "w") as file:
        try:
            json.dump(data, file)
        except OSError:
            pass


def read_json_cache(cache_key: bytes) -> Any | None:
    """
    Read a JSON cache file stored in a temporary directory.

    :param cache_key: hash object to use as a key
    :returns: decoded data or ``None``
    """

    cache = _get_cache_path(cache_key)
    if not cache.is_file():
        return None

    with open(cache) as file:
        return json.load(file)
