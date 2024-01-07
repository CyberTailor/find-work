<!-- SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in> -->
<!-- SPDX-License-Identifier: CC0-1.0 -->

find-work
=========

[![Build Status](https://drone.tildegit.org/api/badges/CyberTaIlor/find-work/status.svg)](https://drone.tildegit.org/CyberTaIlor/find-work)

find-work is a utility for Gentoo repository maintainers that helps them find
ebuilds to improve.


Installing
----------

### Gentoo

```sh
eselect repository enable guru
emaint sync -r guru
emerge dev-util/find-work
```

### Other systems

```sh
pip install find-work --user
sudo make install-data
```


Packaging
---------

You can track new releases using an [atom feed][atom] provided by GitHub.

[atom]: https://github.com/cybertailor/find-work/releases.atom


Contributing
------------

Patches and pull requests are welcome. Please use either [git-send-email(1)][1]
or [git-request-pull(1)][2], addressed to <cyber@sysrq.in>.

If you prefer GitHub-style workflow, use the [mirror repo][gh] to send pull
requests.

Your commit message should conform to the following standard:

```
file/changed: Concice and complete statement of the purpose

This is the body of the commit message.  The line above is the
summary.  The summary should be no more than 72 chars long.  The
body can be more freely formatted, but make it look nice.  Make
sure to reference any bug reports and other contributors.  Make
sure the correct authorship appears.
```

[1]: https://git-send-email.io/
[2]: https://git-scm.com/docs/git-request-pull
[gh]: http://github.com/cybertailor/find-work


IRC
---

You can join the `#find-work` channel either on [Libera Chat][libera] or
[via Matrix][matrix].

[libera]: https://libera.chat/
[matrix]: https://matrix.to/#/#find-work:sysrq.in


License
-------

WTFPL
