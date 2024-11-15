# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Utility functions and classes.
"""

import re
import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiohttp
from pydantic import validate_call

from find_work.core.constants import USER_AGENT

with warnings.catch_warnings():
    # Disable annoying warning shown to LibreSSL users
    warnings.simplefilter("ignore")
    import requests

_pkgname_re = r"[\w][-+\w]*?"
_version_re = r"""
    \d+(\.\d+)*
    [a-z]?
    (_(alpha|beta|pre|rc|p)\d*)*
    (-r\d+)?
"""
_end_marker_re = r"""
    # must be followed by whitespace, punctuation or end of line
    (?=$|[:;,\s])
"""

_pkgname_ver_re = r"""
    {0}
    -
    {1}
""".format(_pkgname_re, _version_re)
_pkg_re = r"""
    (?P<category>
        [\w][-+.\w]*
    )
    /
    (?P<pn>
        {0}
    )
    (
        -
        (?P<pv>
            {1}
        )
    )?

    {2}
""".format(_pkgname_re, _version_re, _end_marker_re)

pkgname_re = re.compile(_pkgname_re, re.ASCII | re.VERBOSE)
pkgname_ver_re = re.compile(_pkgname_ver_re, re.ASCII | re.VERBOSE)
pkg_re = re.compile(_pkg_re, re.ASCII | re.VERBOSE)


@validate_call(validate_return=True)
def extract_package_name(line: str) -> str | None:
    """
    Find the first CPV-looking thing in a line and try to extract its package
    name.

    :param line: line to match
    :return: qualified package name or ``None``

    >>> extract_package_name("Please bump Firefox") is None
    True
    >>> extract_package_name("sys-kernel/genkernel-4-3-10 is an invalid atom") is None
    True
    >>> extract_package_name("media-libs/libjxl: version bump")
    'media-libs/libjxl'
    >>> extract_package_name(">=dev-java/ant-1.10.14: version bump - needed for jdk:21")
    'dev-java/ant'
    >>> extract_package_name("dev-cpp/std-format-0_pre20220112-r1 fails to compile")
    'dev-cpp/std-format'
    >>> extract_package_name("app-foo/bar-2-baz-4.0: version bump")
    'app-foo/bar-2-baz'
    """

    if (match := pkg_re.search(line)) is None:
        return None

    category = match.group("category")
    name = match.group("pn")

    # Filter out any false positives
    if not pkgname_re.fullmatch(name):
        return None

    # Package names "must not end in a hyphen followed by anything
    # matching the version syntax" (PMS 3.1.2)
    if pkgname_ver_re.fullmatch(name):
        return None

    return "/".join([category, name])


@asynccontextmanager
async def aiohttp_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """
    Construct an :py:class:`aiohttp.ClientSession` object with out settings.
    """

    headers = {"user-agent": USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=30)
    session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    try:
        yield session
    finally:
        await session.close()


def requests_session() -> requests.Session:
    """
    Construct an :py:class:`requests.Session` object with out settings.
    """
    session = requests.Session()
    session.headers["user-agent"] = USER_AGENT
    return session
