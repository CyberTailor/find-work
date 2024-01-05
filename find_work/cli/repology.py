# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" CLI subcommands for everything Repology. """

import click

from find_work.cli import Options


@click.command()
@click.pass_obj
def outdated(options: Options) -> None:
    """ Find outdated packages. """
