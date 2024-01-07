# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import tempfile
from pathlib import Path

from find_work.utils import _get_cache_path


def test_get_cache_path(monkeypatch):
    monkeypatch.setattr(tempfile, "gettempdir", lambda: "/tmp")

    assert (
        _get_cache_path(b"test") ==
        Path("/tmp/find-work/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08.json")
    )
