# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from find_work.app.config.types import (
    ConfigAliasCliFlag,
    ConfigAliasCliOption,
    ConfigAliasLiteralValue,
    ConfigRoot,
)


def test_alias_empty():
    assert not ConfigRoot.model_validate({}).aliases


def test_alias_type_error():
    with pytest.raises(ValidationError):
        ConfigRoot.model_validate({"alias": "hello"}).aliases


def test_alias_sample():
    path = Path(__file__).parent / "data" / "alias_sample.toml"
    with open(path, "rb") as file:
        toml = tomllib.load(file)
    config = ConfigRoot.model_validate(toml)

    assert len(config.aliases) == 1
    alias_name, alias_obj = config.aliases.popitem()

    assert alias_name == "foo"
    assert alias_obj.command == "sample:bar"
    assert alias_obj.description == "Sample alias."
    assert alias_obj.shortcuts == {"smpl"}

    assert len(alias_obj.options) == 1
    options = alias_obj.options["sample"].root

    simple_opt = options["simple"]
    assert isinstance(simple_opt, ConfigAliasLiteralValue)
    assert simple_opt.model_dump() == ("simple", "value")

    option_opt = options["option"]
    assert isinstance(option_opt, ConfigAliasCliOption)
    assert len(option_opt.root) == 1
    assert option_opt.names == {"-o", "--option"}

    flag_opt = options["flag"]
    assert isinstance(flag_opt, ConfigAliasCliFlag)
    assert len(flag_opt.root) == 1
    assert flag_opt.names == {"-f", "--flag"}


def test_flag_empty():
    assert not ConfigRoot.model_validate({}).flags


def test_flag_type_error():
    with pytest.raises(ValidationError):
        ConfigRoot.model_validate({"flag": "hello"}).flags


def test_flag_sample():
    path = Path(__file__).parent / "data" / "flag_sample.toml"
    with open(path, "rb") as file:
        toml = tomllib.load(file)
    config = ConfigRoot.model_validate(toml)

    assert len(config.flags) == 1
    flag_name, flag_obj = config.flags.popitem()

    assert flag_name == "sample"
    assert flag_obj.description == "Sample global flag."
    assert flag_obj.shortcuts == {"-s"}
    assert flag_obj.params == {"key1": "val1", "key2": "val2"}
