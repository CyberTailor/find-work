# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

from sortedcontainers import SortedSet
from repology_client.types import Package

from find_work.types import VersionBump
from find_work.cli import Options
from find_work.cli.repology import _collect_version_bumps


def test_collect_version_bumps():
    options = Options()
    options.only_installed = False
    options.repology.repo = "example_linux"

    data = [
        {
            Package(
                repo="example_linux",
                visiblename="dev-util/examplepkg",
                version="1",
                status="outdated",
            ),
            Package(
                repo="example_bsd",
                visiblename="python-examplepkg",
                version="2",
                status="newest",
            ),
            Package(
                repo="example_macos",
                visiblename="py3-examplepkg",
                version="1",
                status="outdated",
            ),
        },
    ]

    expected = SortedSet([VersionBump("dev-util/examplepkg", "1", "2")])
    assert expected == _collect_version_bumps(data, options)


def test_collect_version_bumps_multi_versions():
    options = Options()
    options.only_installed = False
    options.repology.repo = "example_linux"

    data = [
        {
            Package(
                repo="example_linux",
                visiblename="dev-util/examplepkg",
                version="0",
                status="outdated",
            ),
            Package(
                repo="example_linux",
                visiblename="dev-util/examplepkg",
                version="1",
                status="outdated",
            ),
            Package(
                repo="example_bsd",
                visiblename="python-examplepkg",
                version="2",
                status="newest",
            ),
            Package(
                repo="example_macos",
                visiblename="py3-examplepkg",
                version="1",
                status="outdated",
            ),
        },
    ]

    expected = SortedSet([VersionBump("dev-util/examplepkg", "1", "2")])
    assert expected == _collect_version_bumps(data, options)


def test_collect_version_bumps_multi_names():
    options = Options()
    options.only_installed = False
    options.repology.repo = "example_linux"

    data = [
        {
            Package(
                repo="example_linux",
                visiblename="dev-util/examplepkg",
                version="0 pre-release",
                origversion="0",
                status="outdated",
            ),
            Package(
                repo="example_linux",
                visiblename="dev-util/examplepkg",
                version="1",
                status="outdated",
            ),
            Package(
                repo="example_linux",
                visiblename="dev-util/examplepkg-bin",
                version="1",
                status="outdated",
            ),
            Package(
                repo="example_bsd",
                visiblename="python-examplepkg",
                version="2",
                status="newest",
            ),
            Package(
                repo="example_macos",
                visiblename="py3-examplepkg",
                version="1",
                status="outdated",
            ),
        },
    ]

    expected = SortedSet([
        VersionBump("dev-util/examplepkg", "1", "2"),
        VersionBump("dev-util/examplepkg-bin", "1", "2"),
    ])
    assert expected == _collect_version_bumps(data, options)
