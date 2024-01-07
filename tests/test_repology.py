# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

from sortedcontainers import SortedSet
from repology_client.types import Package

from find_work.cli import Options
from find_work.cli.repology import (
    VersionBump,
    _collect_version_bumps,
    _projects_from_json,
    _projects_to_json,
)


def test_projects_json_roundtrip():
    pkg1 = Package(
        repo="gentoo",
        visiblename="www-client/firefox",
        version="9999",
        status="test",
        licenses=frozenset(["GPL-2", "LGPL-2.1", "MPL-2.0"]),
    )
    pkg2 = Package(
        repo="gentoo",
        visiblename="www-client/firefox-bin",
        version="9999",
        status="test",
        licenses=frozenset(["GPL-2", "LGPL-2.1", "MPL-2.0"]),
    )
    data = {"firefox": {pkg1, pkg2}}
    assert data == _projects_from_json(_projects_to_json(data))


def test_collect_version_bumps():
    options = Options()
    options.only_installed = False
    options.repology.repo = "example_linux"

    pkg1 = Package(
        repo="example_linux",
        visiblename="examplepkg",
        version="1",
        status="outdated",
    )
    pkg2 = Package(
        repo="example_bsd",
        visiblename="python-examplepkg",
        version="2",
        status="newest",
    )
    pkg3 = Package(
        repo="example_macos",
        visiblename="py3-examplepkg",
        version="1",
        status="outdated",
    )
    data = [{pkg1, pkg2, pkg3}]

    expected = SortedSet([VersionBump("examplepkg", "1", "2")])
    assert expected == _collect_version_bumps(data, options)