# Implementation Plan: Add Ruff Lint

## Overview

Wire ruff into the repo so `make be.lint` works end-to-end. The Makefile already references `$(VENV_DIR)/bin/ruff` and `backend.mk` already has the `be.lint` target — what's missing is the ruff config, a dev-deps file to pin ruff, and a venv-setup make target to install it.

## Architecture Decisions

- Config lives in `pyproject.toml` (standard Python tooling home; no extra config file needed)
- Dev deps pinned in `requirements-dev.txt` (stdlib-only project has no `requirements.txt`; keeps prod deps separate)
- Venv setup target added to `backend.mk` as `be.setup` (consistent with existing `be.lint` naming)

## Task List

### Phase 1: Config and Deps

- [ ] Task 1: Add `pyproject.toml` with ruff config
- [ ] Task 2: Add `requirements-dev.txt` pinning ruff

### Checkpoint: Config

- [ ] `pyproject.toml` parses cleanly (`python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`)

### Phase 2: Make Target

- [ ] Task 3: Add `be.setup` target to `backend.mk`

### Phase 3: Verify

- [ ] Task 4: Run `make be.setup && make be.lint` end-to-end, fix any lint issues in `verify_deck.py`

### Checkpoint: Complete

- [ ] `make be.lint` exits 0 on clean code
- [ ] `make be.setup` is idempotent (safe to run twice)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ruff finds real issues in verify_deck.py | Low | Fix inline; file is small |
| Python < 3.11 lacks `tomllib` for checkpoint check | Low | Use `ruff --version` as sanity check instead |
