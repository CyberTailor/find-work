# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
All important constants in one place.
"""

#: Application package name.
PACKAGE = "find-work"

#: Application version.
VERSION = "0.990.0"

#: Application homepage.
HOMEPAGE = "https://find-work.sysrq.in"

#: Application affiliation.
ENTITY = "sysrq.in"

#: Application's User-agent header.
USER_AGENT = f"Mozilla/5.0 (compatible; {PACKAGE}/{VERSION}; +{HOMEPAGE})"

#: Default config file name.
DEFAULT_CONFIG = "default_config.toml"

#: Entry point for CLI plugins.
PLUGINS_ENTRY_POINT = "find_work.plugins.v1"

#: Entry point for result reporters.
REPORTERS_ENTRY_POINT = "find_work.reporters.v1"
