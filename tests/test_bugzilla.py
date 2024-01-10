# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import json
from pathlib import Path

import pytest

from find_work.cli.bugzilla import (
    _bugs_from_json,
    _bugs_to_json,
)


@pytest.mark.vcr
def test_bugs_json_roundtrip():
    with open(Path(__file__).parent / "data" / "bug74072.json") as file:
        data: list[dict] = json.load(file)
    assert data == _bugs_to_json(_bugs_from_json(data))
