# Implementation Plan: Single-Card Scryfall Verification CLI

## Overview

Add `verify_card.py`, a standalone script that looks up one card by exact name
on Scryfall and prints either a rich emoji-tagged table (found) or a clear
failure message (not found). Mirrors `verify_deck.py`'s check/format/report
layering and stdlib-only runtime policy. Full detail: `SPEC.md`.

## Architecture Decisions

- New flat script (`verify_card.py`), not a subcommand of `verify_deck.py` —
  keeps each CLI single-purpose, matches existing repo pattern (decided in SPEC.md).
- 429 backoff/retry logic is copied from `verify_deck.check_card`, not shared
  via a new `lib/` module — premature abstraction for ~15 lines, per CLAUDE.md
  "no gratuitous abstraction." Revisit if a third script needs it.
- No third-party table library — stdlib f-string formatting is enough for a
  fixed 7-row table.

## Task List

### Phase 1: Fetch layer

- [x] Task 1: `fetch_card(name)` — exact-match lookup, success/404/429/HTTP/network paths

### Checkpoint: Fetch layer
- [x] `make be.test` green, `fetch_card` fully covered

### Phase 2: Format layer

- [x] Task 2: `render_card_table(data)` — pure formatting function
- [x] Task 3: `render_not_found(name, detail)` — pure formatting function

### Checkpoint: Format layer
- [x] `make be.test` green, both render functions fully covered

### Phase 3: Report layer (wiring)

- [x] Task 4: `main()` — argparse, fetch → render → print, exit codes

### Checkpoint: Integration
- [x] `make be.test` green at 100% coverage for `verify_card.py`
- [x] `make be.lint` exits 0
- [x] Manual run against real Scryfall: found card, not-found card

### Phase 4: Docs

- [x] Task 5: Update `CLAUDE.md` (Codebase Map + Architecture) for the new script, archive `SPEC.md` to `docs/specs/verify-card-cli.md`

### Checkpoint: Complete
- [x] All SPEC.md acceptance criteria met
- [x] Root `SPEC.md` archived to `docs/specs/verify-card-cli.md`
- [x] Ready for review / PR

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Double-faced card fallback (`card_faces[0]`) logic untested against a real oddball card | Med | Craft a synthetic double-faced fixture dict in tests; don't rely on live API shape drift |
| Duplicating retry logic from `verify_deck.py` drifts out of sync over time | Low | Accepted per SPEC.md boundary; revisit only if a third script needs it |

## Open Questions

None — SPEC.md resolved match mode, table fields, and entry-point shape.
