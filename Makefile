# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

PROG = find-work

PREFIX      ?= /usr/local
MANDIR      ?= $(PREFIX)/share/man
BASHCOMPDIR ?= $(PREFIX)/share/bash-completion/completions
ZSHCOMPDIR  ?= $(PREFIX)/share/zsh/site-functions
FISHCOMPDIR ?= $(PREFIX)/share/fish/vendor_completions.d

INSTALL      ?= install
INSTALL_DATA ?= $(INSTALL) -m 0644

help:
	@echo  'usage: make [target] ...'
	@echo
	@echo  'suggested targets:'
	@echo  'install-man	- Install manpages'
	@echo  'install-comp	- Install shell completions'
	@echo  'install-data	- Shorhand for "install-man install-comp"'

install-data: install-man install-comp

install-man:
	mkdir -p $(DESTDIR)$(MANDIR)/man1
	$(INSTALL_DATA) man/$(PROG).1 $(DESTDIR)$(MANDIR)/man1

install-comp: install-bashcomp install-zshcomp install-fishcomp

install-bashcomp: completions/$(PROG).bash
	mkdir -p $(DESTDIR)$(BASHCOMPDIR)
	$(INSTALL_DATA) $< $(DESTDIR)$(BASHCOMPDIR)/$(PROG)

install-zshcomp: completions/$(PROG).zsh
	mkdir -p $(DESTDIR)$(ZSHCOMPDIR)
	$(INSTALL_DATA) $< $(DESTDIR)$(ZSHCOMPDIR)/_$(PROG)

install-fishcomp: completions/$(PROG).fish
	mkdir -p $(DESTDIR)$(FISHCOMPDIR)
	$(INSTALL_DATA) $< $(DESTDIR)$(FISHCOMPDIR)/$(PROG).fish

completions/$(PROG).bash:
	mkdir -p completions
	_FIND_WORK_COMPLETE=bash_source $(PROG) > $@

completions/$(PROG).zsh:
	mkdir -p completions
	_FIND_WORK_COMPLETE=zsh_source $(PROG) > $@

completions/$(PROG).fish:
	mkdir -p completions
	_FIND_WORK_COMPLETE=fish_source $(PROG) > $@

.PHONY: help install-data install-man install-comp install-bashcomp install-zshcomp install-fishcomp
