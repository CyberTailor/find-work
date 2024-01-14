# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" Configuration parsing and validation. """

from abc import ABC
from functools import cached_property
from typing import Any

from find_work.types import CliOptionKind


# FIXME: Find out how to use Pydantic for type validation
class ConfigBase(ABC):
    """ Base class for all configuration objects. """

    _obj: dict
    _context: str

    def _type_error(self, key: str, hint: type) -> TypeError:
        message = f"value must be of type `{hint.__name__}`"
        return TypeError(f"{self._context}{key}: {message}")

    def _value_error(self, key: str, message: str) -> ValueError:
        return ValueError(f"{self._context}{key}: {message}")

    def _ensure_type(self, key: str, value: Any, hint: type) -> None:
        if not isinstance(value, hint):
            raise self._type_error(key, hint)

    def _get(self, key: str, hint: type, *, default: Any = None) -> Any:
        value = self._obj.get(key, default)
        self._ensure_type(key, value, hint)
        return value


class ConfigModuleOption(ConfigBase):
    """ Basic module option parser and validator. """

    def __init__(self, module: str, name: str, value: str | dict, *,
                 context: str = ""):
        self.module: str = module
        self.name: str = name

        self._obj: dict = {}
        self._value: str | dict = value
        self._context: str = f"{context}.{module}."

    @cached_property
    def kind(self) -> CliOptionKind:
        """
        Load option's kind from the configuration.
        """

        if isinstance(self._value, dict):
            value = self._value.copy()  # type: ignore
            match value.popitem()[0]:
                case "option":
                    return CliOptionKind.OPTION
                case "flag":
                    return CliOptionKind.FLAG
                case _:
                    self._value_error(self.name, "unknown value type")
        return CliOptionKind.SIMPLE

    @cached_property
    def value(self) -> Any:
        """
        Load option's value from the configuration.
        """

        match self.kind:
            case CliOptionKind.SIMPLE:
                return self._value
            case CliOptionKind.OPTION:
                return self._value["option"]  # type: ignore
            case CliOptionKind.FLAG:
                return self._value["flag"]  # type: ignore
            case _:
                self._value_error(self.name, "unknown value type")


class ConfigAlias(ConfigBase):
    """ Basic custom aliases parser and validator. """

    def __init__(self, name: str, params: dict, *, context: str = ""):
        self.name: str = name

        self._obj: dict = params
        self._context: str = f"{context}.{name}."

    @cached_property
    def options(self) -> list[ConfigModuleOption]:
        """
        Load new command's module options from the configuration.
        """

        key = "options"
        value = self._get(key, dict, default={})
        if len(value) > 1:
            raise self._value_error(key, "mixed module options are disallowed")
        if len(value) == 0:
            return []

        result: list[ConfigModuleOption] = []
        module, opts = value.popitem()
        self._ensure_type(key, module, str)
        self._ensure_type(key, opts, dict)

        for opt_name, opt_value in opts.items():
            if isinstance(opt_value, dict) and len(opt_value) != 1:
                raise self._value_error(f"module.{opt_name}", "invalid value")
            result.append(ConfigModuleOption(module, opt_name, opt_value,
                                             context=self._context + "options"))
        return result

    @cached_property
    def command(self) -> str:
        """
        Load new command's function from the configuration.
        """

        return self._get("command", str)

    @cached_property
    def description(self) -> str:
        """
        Load new command's help text from the configuration.
        """

        return self._get("description", str)

    @cached_property
    def shortcuts(self) -> list[str]:
        """
        Load new command's aliases from the configuration.
        """

        return self._get("shortcuts", list, default=[])


class Config(ConfigBase):
    """ Basic configuration parser and validator. """

    def __init__(self, config: dict):
        self._obj: dict = config
        self._context: str = ""

    @cached_property
    def aliases(self) -> list[ConfigAlias]:
        """
        Load custom aliases from the configuration.
        """

        result: list[ConfigAlias] = []
        for name, params in self._get("alias", dict, default={}).items():
            result.append(ConfigAlias(name, params,
                                      context=self._context + "alias"))
        return result
