# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Utility functions and classes. """

import re
import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiohttp

from find_work.constants import USER_AGENT

with warnings.catch_warnings():
    # Disable annoying warning shown to LibreSSL users
    warnings.simplefilter("ignore")
    import requests

pkg_re = re.compile(r"""
    (?P<category>
        [\w][-+.\w]*
    )
    /
    (?P<pv>
        [\w][-+.\w]*
    )

    # must be followed by whitespace, punctuation or end of line
    (?=$|[:;,\s])
    """, re.ASCII | re.VERBOSE)
pkgname_re = re.compile(r"[\w][-+\w]*")
version_re = re.compile(r"""
    \d+(\.\d+)*
    [a-z]?
    (_(alpha|beta|pre|rc|p)\d*)*
    (-r\d+)?

    # must be followed by whitespace, punctuation or end of line
    (?=$|[:;,\s])
    """, re.ASCII | re.VERBOSE)


def _guess_package_name(pv: str) -> str:
    parts = pv.split("-")
    match len(parts):
        case 0:
            raise ValueError("Empty match")
        case 1:
            return pv
        case 2:
            if version_re.fullmatch(parts[-1]):
                return "-".join(parts[:-1])
            return pv

    # watch out, revision could be present!
    for ver_start in [-2, -1]:
        ver = "-".join(parts[ver_start:])
        if not version_re.fullmatch(ver):
            # something like "-bar" or "-r1"
            continue

        if len(parts[:ver_start]) > 1:
            # Package names "must not end in a hyphen followed by anything
            # matching the version syntax" (PMS 3.1.2)
            name_end = parts[ver_start - 1]
            if version_re.fullmatch(name_end):
                continue

        return "-".join(parts[:ver_start])
    return pv


def extract_package_name(line: str) -> str | None:
    """
    Find the first CPV-looking thing in a line and try to extract its package
    name.

    :param line: line to match
    :return: qualified package name or ``None``

    >>> extract_package_name("Please bump Firefox") is None
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
    name = _guess_package_name(match.group("pv"))

    # filter out false positives
    if not pkgname_re.fullmatch(name):
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
