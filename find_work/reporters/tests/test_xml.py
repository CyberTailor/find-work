# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import textwrap

import pytest

from find_work.core.cli.options import MainOptions
from find_work.core.types.results import (
    BugView,
    PkgcheckResult,
    PkgcheckResultPriority,
    PkgcheckResultsGroup,
    VersionBump,
)

from find_work.reporters.xml import (
    XmlBugViewReporter,
    XmlPkgcheckResultReporter,
    XmlVersionBumpReporter,
)


def test_version_bump_none(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("lxml")

    with XmlVersionBumpReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "xml"
        assert reporter.result_type == VersionBump
        assert reporter.active

    out = capfd.readouterr().out.strip("\n")
    expected = "<FindWork/>"
    assert out == expected


def test_version_bump(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("lxml")

    with XmlVersionBumpReporter(MainOptions()) as reporter:
        reporter.add_result(VersionBump("dev-foo/bar", "1.0", "2.0"))

    out = capfd.readouterr().out.strip("\n")
    expected = textwrap.dedent(
        """
        <FindWork>
            <VersionBump>
                <Atom>dev-foo/bar</Atom>
                <OldVersion>1.0</OldVersion>
                <NewVersion>2.0</NewVersion>
            </VersionBump>
        </FindWork>
        """
    ).strip("\n")

    assert out == expected


def test_bug_view_none(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("lxml")

    with XmlBugViewReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "xml"
        assert reporter.result_type == BugView
        assert reporter.active

    out = capfd.readouterr().out.strip("\n")
    expected = "<FindWork/>"
    assert out == expected


def test_bug_view(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("lxml")

    with XmlBugViewReporter(MainOptions()) as reporter:
        reporter.add_result(BugView(1, "1970-01-01", "larry@gentoo.org", "Moo!"))

    out = capfd.readouterr().out.strip("\n")
    expected = textwrap.dedent(
        """
        <FindWork>
            <Bug>
                <Id>1</Id>
                <LastChangeDate>1970-01-01</LastChangeDate>
                <AssignedTo>larry@gentoo.org</AssignedTo>
                <Summary>Moo!</Summary>
            </Bug>
        </FindWork>
        """
    ).strip("\n")

    assert out == expected


def test_pkgcheck_results_none(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("lxml")

    with XmlPkgcheckResultReporter(MainOptions()) as reporter:
        assert reporter.reporter_name == "xml"
        assert reporter.result_type == PkgcheckResultsGroup
        assert reporter.active

    out = capfd.readouterr().out.strip("\n")
    expected = "<FindWork/>"
    assert out == expected


def test_pkgcheck_results(capfd: pytest.CaptureFixture[str]):
    pytest.importorskip("lxml")

    with XmlPkgcheckResultReporter(MainOptions()) as reporter:
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

    out = capfd.readouterr().out.strip("\n")
    expected = textwrap.dedent(
        """
        <FindWork>
            <PkgcheckResults>
                <Atom>dev-foo/bar</Atom>
                <Result>
                    <Level color="red">error</Level>
                    <Name>BadEbuildVoodoo</Name>
                    <Description>Shame on you!</Description>
                </Result>
                <Result>
                    <Level color="cyan">style</Level>
                    <Name>MinorNitpick</Name>
                    <Description>You should not do this.</Description>
                </Result>
            </PkgcheckResults>
        </FindWork>
        """
    ).strip("\n")

    assert out == expected
