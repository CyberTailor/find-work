# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Configuration file validation implemented with Pydantic models.
"""

from datetime import date, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel

#: Basic TOML types.
BasicTypes = str | int | float | bool | date | time | datetime


class ConfigAliasCliOption(RootModel[dict[Literal["option"], frozenset[str]]]):
    """
    Basic value command line option.
    """

    @property
    def names(self) -> frozenset[str]:
        """
        Names for a new command line option.
        """

        return self.root["option"]


class ConfigAliasCliFlag(RootModel[dict[Literal["flag"], frozenset[str]]]):
    """
    Boolean flag command line option.
    """

    @property
    def names(self) -> frozenset[str]:
        """
        Names for a new command line flag.
        """

        return self.root["flag"]


class ConfigAliasLiteralValue(
    RootModel[BasicTypes
              | tuple["ConfigAliasLiteralValue", ...]
              | dict[BasicTypes, "ConfigAliasLiteralValue"]]):
    """
    Value statically specified in the config.
    """


#: Value dynamically obtained from CLI.
ConfigAliasCliValue = ConfigAliasCliOption | ConfigAliasCliFlag

#: Acceptable value for option overrides.
ConfigAliasValue = ConfigAliasCliValue | ConfigAliasLiteralValue


class ConfigAliasOptions(RootModel[dict[str, ConfigAliasValue]]):
    """
    Option overrides specified in a custom command.
    """


class ConfigFlag(BaseModel):
    """
    This model defines custom global flags.
    """
    model_config = ConfigDict(extra="forbid")

    #: Help text for this global option.
    description: str

    #: Aliases of this global option.
    shortcuts: frozenset[str] = frozenset()

    #: Global options overrides.
    params: dict[str, Any] = Field(min_length=1)


class ConfigAlias(BaseModel):
    """
    This model defines custom commands (aliases).
    """
    model_config = ConfigDict(extra="forbid")

    #: Import name of the target command.
    command: str

    #: Help text for this custom command.
    description: str

    #: Aliases of this custom command.
    shortcuts: frozenset[str] = frozenset()

    #: Option overrides for this custom command.
    options: dict[str, ConfigAliasOptions] = Field(min_length=1, max_length=1)


class ConfigRoot(BaseModel):
    """
    This model defines top level configuration file entries.
    """
    model_config = ConfigDict(extra="allow")

    #: Custom global flags.
    flags: dict[str, ConfigFlag] = Field(alias="flag", default_factory=dict)

    #: Custom commands (aliases).
    aliases: dict[str, ConfigAlias] = Field(alias="alias", default_factory=dict)
