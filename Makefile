# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

PROG = find-work
BIN  = $(PROG)

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
	@echo  'completions	- Build shell completions'
	@echo  'install-man	- Install manpages'
	@echo  'install-comp	- Install shell completions'
	@echo  'install-data	- Shorhand for "install-man install-comp"'

completions: completions/$(PROG).bash completions/$(PROG).zsh completions/$(PROG).fish

install-data: install-man install-comp

install-comp: install-bashcomp install-zshcomp install-fishcomp

install-man:
	mkdir -p $(DESTDIR)$(MANDIR)/man1
	$(INSTALL_DATA) man/$(PROG).1 $(DESTDIR)$(MANDIR)/man1

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
	_FIND_WORK_COMPLETE=bash_source $(BIN) > $@

completions/$(PROG).zsh:
	mkdir -p completions
	_FIND_WORK_COMPLETE=zsh_source $(BIN) > $@

completions/$(PROG).fish:
	mkdir -p completions
	_FIND_WORK_COMPLETE=fish_source $(BIN) > $@

.PHONY: help completions install-data install-man install-comp install-bashcomp install-zshcomp install-fishcomp
