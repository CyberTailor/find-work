# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import pytest
from pydantic import TypeAdapter

from find_work.core.cli.options import MainOptions
from find_work.core.types.results import (
    BugView,
    PkgcheckResult,
    PkgcheckResultPriority,
    PkgcheckResultsGroup,
    VersionBump,
)

from find_work.reporters.json import (
    JsonBugViewReporter,
    JsonPkgcheckResultReporter,
    JsonVersionBumpReporter,
)


def test_version_bump_none(capfd: pytest.CaptureFixture[str]):
    with JsonVersionBumpReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "json"
        assert reporter.result_type == VersionBump
        assert reporter.active

    out = capfd.readouterr().out.strip("\n")
    expected = "[]"
    assert out == expected


def test_version_bump_roundtrip(capfd: pytest.CaptureFixture[str]):
    result = VersionBump("dev-foo/bar", "1.0", "2.0")
    with JsonVersionBumpReporter(MainOptions()) as reporter:
        reporter.add_result(result)

    out = capfd.readouterr().out
    assert TypeAdapter(list[VersionBump]).validate_json(out) == [result]


def test_bug_view_none(capfd: pytest.CaptureFixture[str]):
    with JsonBugViewReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "json"
        assert reporter.result_type == BugView
        assert reporter.active

    out = capfd.readouterr().out.strip("\n")
    expected = "[]"
    assert out == expected


def test_bug_view_roundtrip(capfd: pytest.CaptureFixture[str]):
    result = BugView(1, "1970-01-01", "larry@gentoo.org", "Moo!")
    with JsonBugViewReporter(MainOptions()) as reporter:
        reporter.add_result(result)

    out = capfd.readouterr().out
    assert TypeAdapter(list[BugView]).validate_json(out) == [result]


def test_pkgcheck_results_none(capfd: pytest.CaptureFixture[str]):
    with JsonPkgcheckResultReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "json"
        assert reporter.result_type == PkgcheckResultsGroup
        assert reporter.active

    out = capfd.readouterr().out.strip("\n")
    expected = "[]"
    assert out == expected


def test_pkgcheck_results_roundtrip(capfd: pytest.CaptureFixture[str]):
    result = {
        "atom": "dev-foo/bar",
        "results": {
            PkgcheckResult(
                PkgcheckResultPriority("style", "cyan"),
                "MinorNitpick",
                "You should not do this.",
            ),
            PkgcheckResult(
                PkgcheckResultPriority("error", "red"),
                "BadEbuildVoodoo",
                "Shame on you!",
            ),
        },
    }
    with JsonPkgcheckResultReporter(MainOptions()) as reporter:
        reporter.add_result(result)

    out = capfd.readouterr().out.strip("\n")
    assert TypeAdapter(list[PkgcheckResultsGroup]).validate_json(out) == [result]
