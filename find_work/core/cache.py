# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Implementation of caching functionality.
"""

import hashlib
import tempfile
from pathlib import Path
from typing import SupportsBytes

from find_work.core.constants import PACKAGE


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
