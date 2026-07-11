# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Single-script Python tool that verifies every card in a Magic: The Gathering deck file exists on Scryfall. No dependencies beyond stdlib.

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
├── pyproject.toml          # Ruff lint config (E, F, W, I, UP; 100-char lines)
├── requirements-dev.txt    # Dev dependencies (ruff)
├── Makefile                # Top-level make entrypoint; defines PYTHON, VENV_DIR, RUFF vars
├── .make/
│   ├── backend.mk          # be.setup (venv + install), be.lint (ruff check .)
│   └── base.mk             # help target
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── pull-request.yml  # CI: setup-python → be.setup → be.lint
├── docs/
│   └── python-style.md     # Coding standards; agents must read before writing Python
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

## Pull Requests

Always use `.github/PULL_REQUEST_TEMPLATE.md` as the body structure when creating PRs. Fill in each section ([What], [Why], References) with real content; remove placeholder lines.
