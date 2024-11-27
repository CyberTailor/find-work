# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Results reporter for machine-readable XML output.
"""

from typing import Any, TypeVar

from pydantic import validate_call

from find_work.core.reporters import AbstractReporter
from find_work.core.types.results import (
    BugView,
    PkgcheckResultsGroup,
    VersionBump,
)

try:
    import lxml.etree as ET
    _HAS_LXML = True
except ModuleNotFoundError:
    _HAS_LXML = False

T = TypeVar("T")


class XmlReporter(AbstractReporter[T]):
    """
    XML reporter using the lxml library.
    """

    reporter_name = "xml"
    _root: ET._Element

    def __enter__(self) -> "XmlReporter":
        self._root = ET.Element("FindWork")

        return self

    def __exit__(self, *args: Any) -> None:
        ET.indent(self._root, space=" " * 4, level=0)
        self.options.echo(ET.tostring(self._root, encoding="unicode"))

    @property
    def active(self) -> bool:
        return _HAS_LXML


class XmlVersionBumpReporter(XmlReporter[VersionBump]):
    result_type = VersionBump

    @validate_call
    def add_result(self, item: VersionBump) -> None:
        element = ET.SubElement(self._root, "VersionBump")
        ET.SubElement(element, "Atom").text = item.atom
        ET.SubElement(element, "OldVersion").text = item.old_version
        ET.SubElement(element, "NewVersion").text = item.new_version


class XmlBugViewReporter(XmlReporter[BugView]):
    result_type = BugView

    @validate_call
    def add_result(self, item: BugView) -> None:
        element = ET.SubElement(self._root, "Bug")
        ET.SubElement(element, "Id").text = str(item.bug_id)
        ET.SubElement(element, "LastChangeDate").text = item.last_change_date
        ET.SubElement(element, "AssignedTo").text = item.assigned_to
        ET.SubElement(element, "Summary").text = item.summary


class XmlPkgcheckResultReporter(XmlReporter[PkgcheckResultsGroup]):
    result_type = PkgcheckResultsGroup

    def add_result(self, item: PkgcheckResultsGroup) -> None:
        element = ET.SubElement(self._root, "PkgcheckResults")
        ET.SubElement(element, "Atom").text = item["atom"]

        for result in item["results"]:
            result_element = ET.SubElement(element, "Result")
            ET.SubElement(
                result_element, "Level",
                color=result.priority.color
            ).text = result.priority.level
            ET.SubElement(result_element, "Name").text = result.name
            ET.SubElement(result_element, "Description").text = result.desc
