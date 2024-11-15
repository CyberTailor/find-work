# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Console messages.
"""

from enum import Enum, StrEnum

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    """
    Styled message.
    """

    #: Message text.
    text: str

    #: Message foreground color.
    color: str


class Status(StrEnum):
    """
    Messages for ongoing tasks.
    """

    #: Reading cache file.
    CACHE_READ = "Checking for cached data"

    #: Deserialization.
    CACHE_LOAD = "Reading data from cache"

    #: Serialization and writing cache file.
    CACHE_WRITE = "Caching data"


class Result(Message, Enum):
    """
    Messages for non-standard command execution results.

    :meta private:
    """

    #: Source didn't return any data.
    EMPTY_RESPONSE = (
        "Hmmm, no data returned. Try again with different arguments.",
        "yellow",
    )

    #: All data returned from source was filtered out.
    NO_WORK = (
        "Congrats! You have nothing to do!",
        "green",
    )
