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

DECK_FILE ?= decks/morska.md

# -----------------------------------------------------------------------------
# [git]
# -----------------------------------------------------------------------------
GIT_SHORT_SHA ?= $(shell git rev-parse --short=7 HEAD)
GIT_FULL_SHA  ?= $(shell git rev-parse HEAD)
GIT_NUM_COMMITS_IN_MAIN ?= $(shell git rev-list --count main)

print-%:
	@echo $($*)

include $(wildcard .make/*.mk)