# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" All important constants in one place. """

# Application package name.
PACKAGE = "find-work"

# Application version.
VERSION = "0.3.0"

# Application homepage.
HOMEPAGE = "https://find-work.sysrq.in"

# Application's User-agent header.
USER_AGENT = f"Mozilla/5.0 (compatible; {PACKAGE}/{VERSION}; +{HOMEPAGE})"

# Gentoo Bugzilla location.
BUGZILLA_URL = "https://bugs.gentoo.org"

# Gentoo Packages location.
PGO_BASE_URL = "https://packages.gentoo.org"

# Gentoo Packages API location.
PGO_API_URL = f"{PGO_BASE_URL}/api/graphql/"
