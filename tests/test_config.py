# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import tomllib
from pathlib import Path

import pytest

from find_work.config import Config
from find_work.types._config import CliOptionKind


def test_alias_empty():
    assert not Config({}).aliases


def test_alias_type_error():
    with pytest.raises(TypeError):
        Config({"alias": "hello"}).aliases


def test_alias_sample():
    path = Path(__file__).parent / "data" / "alias_sample.toml"
    with open(path, "rb") as file:
        toml = tomllib.load(file)
    config = Config(toml)

    assert len(config.aliases) == 1
    alias = config.aliases.pop()

    assert alias.name == "sample"
    assert alias.command == "find_work.cli.sample.sample"
    assert alias.description == "Sample alias."
    assert alias.shortcuts == ["smpl"]

    simple_opt = [opt for opt in alias.options if opt.name == "simple"]
    assert len(simple_opt) == 1
    assert simple_opt[0].module == "sample"
    assert simple_opt[0].kind == CliOptionKind.SIMPLE
    assert simple_opt[0].value == "value"

    option_opt = [opt for opt in alias.options if opt.name == "option"]
    assert len(option_opt) == 1
    assert option_opt[0].module == "sample"
    assert option_opt[0].kind == CliOptionKind.OPTION
    assert option_opt[0].value == ["-o", "--option"]

    flag_opt = [opt for opt in alias.options if opt.name == "flag"]
    assert len(flag_opt) == 1
    assert flag_opt[0].module == "sample"
    assert flag_opt[0].kind == CliOptionKind.FLAG
    assert flag_opt[0].value == ["-f", "--flag"]


def test_flag_empty():
    assert not Config({}).flags


def test_flag_type_error():
    with pytest.raises(TypeError):
        Config({"flag": "hello"}).flags


def test_flag_sample():
    path = Path(__file__).parent / "data" / "flag_sample.toml"
    with open(path, "rb") as file:
        toml = tomllib.load(file)
    config = Config(toml)

    assert len(config.flags) == 1
    flag = config.flags.pop()

    assert flag.name == "sample"
    assert flag.description == "Sample global flag."
    assert flag.shortcuts == ["-s"]
    assert flag.params == {"key1": "val1", "key2": "val2"}
