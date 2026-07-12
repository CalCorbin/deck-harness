# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Single-script Python tool that verifies every card in a Magic: The Gathering deck file exists on Scryfall. The runtime script (`verify_deck.py`) has no dependencies beyond stdlib. Dev tooling (lint, test) uses ruff and pytest — see [Testing](#testing) for why pytest was worth the exception.

## Running

```bash
# Verify a deck, print results to stdout
python verify_deck.py decks/morska.md
```

## Deck File Format

Markdown files in `decks/`. Lines matching `<count> [x] <card name>` are parsed; everything else (headers, blanks) is skipped.

```
# Deck Name
1 Sol Ring
5 Forest
1 Koma, Cosmos Serpent
```

## Codebase Map

```
deck-harness/
├── verify_deck.py          # Verification script (parse → check → report)
├── pyproject.toml          # Ruff lint config; pytest + coverage config (100% fail_under)
├── requirements-dev.txt    # Dev dependencies (ruff, pytest, pytest-cov)
├── Makefile                # Top-level make entrypoint; defines PYTHON, VENV_DIR, PYTEST, RUFF vars
├── .make/
│   ├── backend.mk          # be.setup (venv + install), be.lint (ruff check .), be.test (pytest --cov)
│   └── base.mk             # help target
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── pull-request.yml  # CI: setup-python → be.setup → be.lint → be.test
├── docs/
│   ├── python-style.md     # Coding standards; agents must read before writing Python
│   └── ideas/
│       └── testing-framework.md  # Decision record: pytest chosen over stdlib unittest
├── tests/
│   └── test_verify_deck.py # Unit tests for parse/check/report layers, monkeypatched urlopen
└── decks/
    └── morska.md           # Morska, the Unpredictable commander deck
```

## Architecture

`verify_deck.py` has three layers:

1. **Parse** — `parse_deck(path)` applies `LINE_RE` regex, returns `[(count, name), ...]`
2. **Check** — `check_card(name)` hits `SCRYFALL_NAMED` with `?exact=<name>`, returns `(found, detail)`. 404 → not found. 429 → exponential backoff up to 4 attempts (`2^attempt` seconds). Other HTTP errors → `(False, "HTTP <code>")`.
3. **Report** — `main()` drives the loop, prints per-card status, summarizes misses, optionally writes JSON.

Scryfall rate-limit policy: 100ms delay (`REQUEST_DELAY`) between every request, plus backoff on 429.

## Python Style and Linting

Before writing any Python, read `docs/python-style.md`.

## Testing

```bash
make be.setup   # first time only — creates .venv and installs pytest + pytest-cov
make be.test    # run this after every change
```

`make be.test` must exit 0 (100% coverage enforced via `fail_under = 100` in `pyproject.toml`).

`docs/python-style.md` and this repo's global CLAUDE.md both say "prefer stdlib over
third-party unless the gain is substantial." pytest is a deliberate exception, not an
oversight: `parse_deck`/`check_card`/`main` needed TDD-friendly fixtures (`monkeypatch`,
`capsys`) and parametrization for edge cases, and stdlib `unittest` would have meant
hand-rolling that machinery. We stayed disciplined about *not* also pulling in an
HTTP-mocking library (`responses`, `VCR.py`) — `check_card`'s only I/O call
(`urllib.request.urlopen`) is patched directly via `monkeypatch`, so one dependency
exception didn't become three. Full rationale: `docs/ideas/testing-framework.md`.

## Pull Requests

Always use `.github/PULL_REQUEST_TEMPLATE.md` as the body structure when creating PRs. Fill in each section ([What], [Why], References) with real content; remove placeholder lines.
