# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Single-script Python tool that verifies every card in a Magic: The Gathering deck file exists on Scryfall. No dependencies beyond stdlib.

## Running

```bash
# Verify a deck, print results to stdout
python verify_deck.py decks/morska.md

# Also write a JSON report
python verify_deck.py decks/morska.md --json report.json
```

## Deck File Format

Markdown files in `decks/`. Lines matching `<count> [x] <card name>` are parsed; everything else (headers, blanks) is skipped.

```
# Deck Name
1 Sol Ring
5 Forest
1 Koma, Cosmos Serpent
```

## Architecture

`verify_deck.py` has three layers:

1. **Parse** — `parse_deck(path)` applies `LINE_RE` regex, returns `[(count, name), ...]`
2. **Check** — `check_card(name)` hits `SCRYFALL_NAMED` with `?exact=<name>`, returns `(found, detail)`. 404 → not found. 429 → exponential backoff up to 4 attempts (`2^attempt` seconds). Other HTTP errors → `(False, "HTTP <code>")`.
3. **Report** — `main()` drives the loop, prints per-card status, summarizes misses, optionally writes JSON.

Scryfall rate-limit policy: 100ms delay (`REQUEST_DELAY`) between every request, plus backoff on 429.

## Pull Requests

Always use `.github/PULL_REQUEST_TEMPLATE.md` as the body structure when creating PRs. Fill in each section ([What], [Why], References) with real content; remove placeholder lines.
