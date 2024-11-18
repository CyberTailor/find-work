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

from find_work.reporters.html import (
    HtmlBugViewReporter,
    HtmlPkgcheckResultReporter,
    HtmlVersionBumpReporter,
)


def test_version_bump_none(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("tabulate")

    with HtmlVersionBumpReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "html"
        assert reporter.result_type == VersionBump
        assert reporter.active

    out = "".join(capfd.readouterr().out.split())
    assert out.startswith("<table>")
    assert out.endswith("</table>")


def test_version_bump(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("tabulate")

    with HtmlVersionBumpReporter(MainOptions()) as reporter:
        reporter.add_result(VersionBump("dev-foo/bar", "1.0", "2.0"))

    out = "".join(capfd.readouterr().out.split())
    expected = (
        '<table><thead><tr><th>Packagename</th><th>Repositoryversion</th>'
        '<th>Newestversion</th></tr></thead><tbody><tr><td>dev-foo/bar</td>'
        '<td>1.0</td><td>2.0</td></tr></tbody></table>'
    )

    assert out == expected


def test_bug_view_none(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("tabulate")

    with HtmlBugViewReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "html"
        assert reporter.result_type == BugView
        assert reporter.active

    out = "".join(capfd.readouterr().out.split())
    assert out.startswith("<table>")
    assert out.endswith("</table>")


def test_bug_view(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("tabulate")

    with HtmlBugViewReporter(MainOptions()) as reporter:
        reporter.add_result(BugView(1, "1970-01-01", "larry@gentoo.org", "Moo!"))

    out = "".join(capfd.readouterr().out.split())
    expected = (
        '<table><thead><tr><thstyle="text-align:right;">ID</th><th>Changed</th>'
        '<th>Assignee</th><th>Summary</th></tr></thead><tbody><tr>'
        '<tdstyle="text-align:right;">1</td><td>1970-01-01</td>'
        '<td>larry@gentoo.org</td><td>Moo!</td></tr></tbody></table>'
    )

    assert out == expected


def test_pkgcheck_results_none(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("tabulate")

    with HtmlPkgcheckResultReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "html"
        assert reporter.result_type == PkgcheckResultsGroup
        assert reporter.active

    out = "".join(capfd.readouterr().out.split())
    assert len(out) == 0


def test_pkgcheck_results(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("tabulate")

    with HtmlPkgcheckResultReporter(MainOptions()) as reporter:
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

    out = "".join(capfd.readouterr().out.split())
    expected = (
        '<h2>dev-foo/bar</h2><table><thead><tr><th>Level</th><th>Class</th>'
        '<th>Description</th></tr></thead><tbody><tr><td>error</td>'
        '<td>BadEbuildVoodoo</td><td>Shameonyou!</td></tr><tr><td>style</td>'
        '<td>MinorNitpick</td><td>Youshouldnotdothis.</td></tr></tbody></table>'
    )

    assert out == expected
