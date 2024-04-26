# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Internal type definitions for Gentoo Packages GraphQL API, implemented as
Pydantic models.
"""

from pydantic import BaseModel, ConfigDict, Field

from find_work.types import VersionBump


class OutdatedPackage(BaseModel):
    """
    Information from Repology about an outdated package in the Gentoo tree.
    """
    model_config = ConfigDict(frozen=True)

    #: The atom of the affected package.
    atom: str = Field(alias="Atom")

    #: The latest version of the package that is present in the Gentoo tree.
    old_version: str = Field(alias="GentooVersion", default="(unknown)")

    #: The latest version of the package that is present upstream.
    new_version: str = Field(alias="NewestVersion", default="(unknown)")

    @property
    def as_version_bump(self) -> VersionBump:
        """
        Equivalent :py:class:`find_work.types.VersionBump` object.
        """

        return VersionBump(self.atom, self.old_version, self.new_version)


class PkgCheckResult(BaseModel):
    """
    Single warning from pkgcheck for a package version.
    """
    model_config = ConfigDict(frozen=True)

    #: Atom of the package that is affected by this pkgcheck warning.
    atom: str = Field(alias="Atom")

    # Version of the package that is affected by this pkgcheck warning.
    version: str = Field(alias="Version")

    # Message of this warning, e.g. 'uses deprecated EAPI 5'.
    message: str = Field(alias="Message")


class StableCandidate(BaseModel):
    """
    Stabilization candidate representation.
    """
    model_config = ConfigDict(frozen=True)

    #: Category name.
    category: str

    #: Package name.
    package: str

    #: Package version.
    version: str

    #: Pkgcheck message.
    message: str

    @property
    def as_pkgcheck_result(self) -> PkgCheckResult:
        """
        Equivalent :py:class:`PkgCheckResult` object.
        """

        data = {
            "Atom": "/".join([self.category, self.package]),
            "Version": self.version,
            "Message": self.message,
        }
        return PkgCheckResult.model_validate(data)


class GraphQlData(BaseModel):
    """
    Data returned by GraphQL.
    """

    #: Results of outdatedPackages query.
    outdated: frozenset[OutdatedPackage] = Field(alias="outdatedPackages",
                                                 default=frozenset())

    #: Results of pkgCheckResults query.
    pkgcheck: frozenset[PkgCheckResult] = Field(alias="pkgCheckResults",
                                                default=frozenset())


class GraphQlResponse(BaseModel):
    """
    Root GraphQL response.
    """

    data: GraphQlData = Field(default_factory=GraphQlData)
