MAKEFLAGS += --no-print-directory

# -----------------------------------------------------------------------------
# [App]
# -----------------------------------------------------------------------------
APP_NAME ?= deck-harness

# -----------------------------------------------------------------------------
# [Python Settings]
# -----------------------------------------------------------------------------
PYTHON ?= python3
VENV_DIR ?= .venv
PIP ?= $(VENV_DIR)/bin/pip
PYTEST ?= $(VENV_DIR)/bin/pytest
RUFF ?= $(VENV_DIR)/bin/ruff
VERIFY_CARD ?= $(VENV_DIR)/bin/verify-card
VERIFY_DECK ?= $(VENV_DIR)/bin/verify-deck

DECK_FILE ?= decks/morska/card-list.md

# -----------------------------------------------------------------------------
# [git]
# -----------------------------------------------------------------------------
GIT_SHORT_SHA ?= $(shell git rev-parse --short=7 HEAD)
GIT_FULL_SHA  ?= $(shell git rev-parse HEAD)
GIT_NUM_COMMITS_IN_MAIN ?= $(shell git rev-list --count main)

print-%:
	@echo $($*)

-include Makefile.local
include $(wildcard .make/*.mk)