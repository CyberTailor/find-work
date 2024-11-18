# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import pytest

from find_work.core.cli.options import MainOptions
from find_work.core.types.results import (
    BugView,
    PkgcheckResult,
    PkgcheckResultPriority,
    PkgcheckResultsGroup,
    VersionBump,
)

from find_work.reporters.console import (
    ConsoleBugViewReporter,
    ConsolePkgcheckResultReporter,
    ConsoleVersionBumpReporter,
)


def test_version_bump_none(capfd: pytest.CaptureFixture[str]):
    with ConsoleVersionBumpReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "console"
        assert reporter.result_type == VersionBump
        assert reporter.active

    out = " ".join(capfd.readouterr().out.split())
    assert len(out) == 0


def test_version_bump(capfd: pytest.CaptureFixture[str]):
    with ConsoleVersionBumpReporter(MainOptions()) as reporter:
        reporter.add_result(VersionBump("dev-foo/bar", "1.0", "2.0"))

    out = " ".join(capfd.readouterr().out.split())
    expected = "dev-foo/bar 1.0 → 2.0"

    assert out == expected


def test_bug_view_none(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("tabulate")

    with ConsoleBugViewReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "console"
        assert reporter.result_type == BugView
        assert reporter.active

    out = " ".join(capfd.readouterr().out.split())
    assert len(out) == 0


def test_bug_view(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("tabulate")

    with ConsoleBugViewReporter(MainOptions()) as reporter:
        reporter.add_result(BugView(1, "1970-01-01", "larry@gentoo.org", "Moo!"))

    out = " ".join(capfd.readouterr().out.split())
    expected = "1 1970-01-01 larry@gentoo.org Moo!"

    assert out == expected


def test_pkgcheck_results_none(capfd: pytest.CaptureFixture[str]):
    with ConsolePkgcheckResultReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "console"
        assert reporter.result_type == PkgcheckResultsGroup
        assert reporter.active

    out = " ".join(capfd.readouterr().out.split())
    assert len(out) == 0


def test_pkgcheck_results(capfd: pytest.CaptureFixture[str]):
    with ConsolePkgcheckResultReporter(MainOptions()) as reporter:
        reporter.add_result({
            "atom": "dev-foo/bar",
            "results": sorted({
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
            })
        })

    out = " ".join(capfd.readouterr().out.split())
    expected = (
        "dev-foo/bar "
        "BadEbuildVoodoo: Shame on you! "
        "MinorNitpick: You should not do this."
    )

    assert out == expected
