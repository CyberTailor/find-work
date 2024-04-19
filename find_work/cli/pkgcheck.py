# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

""" CLI subcommands for everything pkgcheck. """

import click
import gentoopm
import pkgcheck
from sortedcontainers import SortedDict, SortedSet

from find_work.cli import Message, Options, ProgressDots


def _do_scan(options: Options) -> SortedDict[str, SortedSet]:
    if options.only_installed or options.maintainer:
        pm = gentoopm.get_package_manager()
        if options.maintainer:
            repo_obj = pm.repositories[options.pkgcheck.repo]

    cli_opts = [
        "--repo", options.pkgcheck.repo,
        "--scope", "pkg,ver",
        "--filter", "latest",  # TODO: become version-aware
    ]
    if options.pkgcheck.keywords:
        cli_opts += ["--keywords", ",".join(options.pkgcheck.keywords)]

    data: SortedDict[str, SortedSet] = SortedDict()
    for result in pkgcheck.scan(cli_opts):
        if options.pkgcheck.message not in result.desc:
            continue

        package = "/".join([result.category, result.package])
        if options.only_installed and package not in pm.installed:
            continue
        if options.maintainer:
            for maint in repo_obj.select(package).maintainers:
                if maint.email == options.maintainer:
                    break
            else:
                continue
        data.setdefault(package, SortedSet(key=str)).add(result)
    return data


@click.command()
@click.pass_obj
def scan(options: Options) -> None:
    options.cache_key.feed("scan")
    dots = ProgressDots(options.verbose)

    options.vecho("Scouring the neighborhood", nl=False, err=True)
    with dots():
        data = _do_scan(options)

    if len(data) == 0:
        options.say(Message.NO_WORK)
        return

    for package, results in data.items():
        options.echo()
        options.secho(package, fg="cyan", bold=True)
        for item in results:
            options.echo("\t", nl=False)
            options.secho(item.name, fg=item.color, nl=False)
            options.echo(": ", nl=False)
            options.echo(item.desc)
