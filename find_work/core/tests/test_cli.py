# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>
# No warranty

import pytest

from pydantic import ValidationError

from find_work.core.cli import colors_disabled_by_env
from find_work.core.cli.options import MainOptions


def test_nocolor_undefined(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NOCOLOR", raising=False)
    monkeypatch.delenv("NO_COLOR", raising=False)

    assert not colors_disabled_by_env()


def test_nocolor_defined_empty(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NOCOLOR", raising=False)
    monkeypatch.setenv("NO_COLOR", "")

    assert not colors_disabled_by_env()


def test_nocolor_defined_notempty(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NOCOLOR", raising=False)
    monkeypatch.setenv("NO_COLOR", "0")

    assert colors_disabled_by_env()


def test_options_category_validation():
    MainOptions()
    MainOptions(category="dev-util")

    for cat in ["", "*", "multi//depth"]:
        with pytest.raises(ValidationError):
            MainOptions(category=cat)
