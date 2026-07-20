# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Two Python CLIs that verify Magic: The Gathering card data against Scryfall: `verify_deck.py` checks every card in a deck file, `verify_card.py` looks up one card and prints its details as a rich table. Both live in the `deck_harness` package (`src/deck_harness/`) and are exposed as console scripts (`verify-deck`, `verify-card`) via `pyproject.toml` `[project.scripts]`. Neither script has runtime dependencies beyond stdlib — the packaging itself (`setuptools`, editable install) is build-time only. Dev tooling (lint, test) uses ruff and pytest — see [Testing](#testing) for why pytest was worth the exception.

## Running

```bash
# Verify a deck, print results to stdout
verify-deck decks/morska/card-list.md

# Look up a single card by exact name, print a rich table (or a not-found message)
verify-card "Sol Ring"
```

Requires `make be.setup` (installs `deck-harness` in editable mode) and an active venv, or call `.venv/bin/verify-deck` / `.venv/bin/verify-card` directly.

## Deck File Format

Each deck lives in its own directory under `decks/`, named after the deck, containing a `card-list.md` file. Lines matching `<count> [x] <card name>` are parsed; everything else (headers, blanks) is skipped.

```
# Deck Name
1 Sol Ring
5 Forest
1 Koma, Cosmos Serpent
```

## Suggesting Cards

Before suggesting or adding a card to a deck file in `decks/`, verify it exists on
Scryfall with `make card.verify NAME='<exact card name>'` (or `verify-card
"<exact card name>"`). Do this for every card name before it's proposed to the user or
written into a deck file — never rely on memory/training data for exact card names,
wording, or existence. Card names are easy to misremember or hallucinate (typos, wrong
capitalization, cards from other games, cards that don't exist), and a wrong name added
to a deck file will silently fail `verify_deck.py` later instead of being caught at
suggestion time.

## Codebase Map

```
deck-harness/
├── src/deck_harness/
│   ├── __init__.py
│   ├── verify_deck.py      # Deck-file batch verification (parse → check → report)
│   └── verify_card.py      # Single-card lookup + rich emoji table (fetch → render → report)
├── pyproject.toml          # Package metadata, [project.scripts] entry points; ruff/pytest/coverage config (100% fail_under)
├── requirements-dev.txt    # Dev dependencies (ruff, pytest, pytest-cov)
├── Makefile                # Top-level make entrypoint; defines PYTHON, VENV_DIR, PYTEST, RUFF, VERIFY_CARD, VERIFY_DECK vars
├── .make/
│   ├── backend.mk          # be.setup (venv + install -e .), be.lint (ruff check .), be.test (pytest --cov=deck_harness)
│   ├── cards.mk            # card.verify target
│   └── base.mk             # help target
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── pull-request.yml  # CI: setup-python → be.setup → be.lint → be.test
├── docs/
│   ├── python-style.md     # Coding standards; agents must read before writing Python
│   ├── ideas/
│   │   └── testing-framework.md    # Decision record: pytest chosen over stdlib unittest
│   └── specs/
│       └── verify-card-cli.md      # Archived spec for verify_card.py
├── tests/
│   ├── test_verify_deck.py # Unit tests for parse/check/report layers, monkeypatched urlopen
│   └── test_verify_card.py # Unit tests for fetch/render/report layers, monkeypatched urlopen
└── decks/
    └── morska/
        └── card-list.md    # Morska, the Unpredictable commander deck
```

## Architecture

`verify_deck.py` has three layers:

1. **Parse** — `parse_deck(path)` applies `LINE_RE` regex, returns `[(count, name), ...]`
2. **Check** — `check_card(name)` hits `SCRYFALL_NAMED` with `?exact=<name>`, returns `(found, detail)`. 404 → not found. 429 → exponential backoff up to 4 attempts (`2^attempt` seconds). Other HTTP errors → `(False, "HTTP <code>")`.
3. **Report** — `main()` drives the loop, prints per-card status, summarizes misses, optionally writes JSON.

Scryfall rate-limit policy: 100ms delay (`REQUEST_DELAY`) between every request, plus backoff on 429.

`verify_card.py` has the same three-layer shape, renamed for its single-card scope:

1. **Fetch** — `fetch_card(name)` hits `SCRYFALL_NAMED` with `?exact=<name>`, returns `(found, data)` where `data` is the full Scryfall card object on success or `{"details": ...}` on failure. 404 → not found with Scryfall's suggestion text. 429 → same exponential backoff as `verify_deck.check_card`.
2. **Render** — `render_card_table(data)` and `render_not_found(name, detail)` are pure formatting functions (no I/O), so table layout is unit-tested directly. `render_card_table` falls back to `card_faces[0]` for `mana_cost`/`oracle_text` on double-faced cards, prints `n/a` for a missing USD price, and wraps long oracle text to terminal width.
3. **Report** — `main()` calls fetch → render, prints the result, returns exit code `0` (found) or `1` (not found/error).

`fetch_card`'s retry/backoff logic is intentionally duplicated from `verify_deck.check_card` rather than shared via a new module — extracting ~15 lines into a `lib/` package would be premature abstraction for two call sites (see `docs/specs/verify-card-cli.md` for the full rationale). Revisit only if a third script needs the same retry contract.

Both scripts live in `src/deck_harness/` (standard src-layout) purely as a physical/packaging move — no shared code was introduced. It lets tests import `deck_harness.verify_deck` / `deck_harness.verify_card` without `sys.path` hacks and gives real CLI entry points (`verify-deck`, `verify-card`) via `pyproject.toml` `[project.scripts]`, installed with `pip install -e .` (folded into `make be.setup`).

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
