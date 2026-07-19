# SPEC: Single-Card Scryfall Verification CLI

## Objective

Add `verify_card.py`, a standalone CLI that checks whether one Magic: The Gathering
card name exists on Scryfall and, when found, prints a rich terminal table of its
details. Mirrors `verify_deck.py`'s parse/check/report layering and stdlib-first
dependency policy, but targets a single card instead of a deck file.

## Commands

```bash
python verify_card.py "Sol Ring"
```

- One positional argument: the card name (exact match, case-insensitive per
  Scryfall's `?exact=` semantics).
- Exit code `0` when the card is found, `1` when not found or on error.
- No flags in v1 (no `--json`, no batch mode) — single card, human-readable
  output only. Keeps parity with the narrow scope of the ask.

### Output: card found

Render a bordered table (stdlib `str` formatting, no third-party TUI library)
with one row per field, each row prefixed with an emoji:

| Emoji | Field | Source (Scryfall card object) |
|---|---|---|
| 🃏 | Name | `name` |
| 💠 | Mana Cost | `mana_cost` (fallback: `card_faces[0].mana_cost` for double-faced cards) |
| 📜 | Type | `type_line` |
| ⭐ | Rarity | `rarity` |
| 📦 | Set | `set_name` (`set` code uppercased in parens), e.g. `Commander (CMD)` |
| 📝 | Text | `oracle_text` (fallback: `card_faces[0].oracle_text`), wrapped to terminal width |
| 💵 | Price (USD) | `prices.usd`; if `null`, print `n/a` |

Mana cost symbols (`{1}`, `{U}`, `{R}`, etc.) are printed as-is from Scryfall's
string — no attempt to re-render them as colored glyphs; that's a large scope
increase (parsing `{W}{U}{B}{R}{G}` combinations, hybrid/phyrexian symbols) for
a "read the table" interaction model that doesn't need it.

### Output: card not found

Print a clear, visually distinct failure message (not just a table row) so the
user can't mistake it for a found card, e.g.:

```
❌ "Sol Rign" not found on Scryfall.
   not found — perhaps you meant "Sol Ring"?
```

The `detail` string already returned by Scryfall's 404 body (same shape
`verify_deck.py.check_card` already surfaces) is printed as the suggestion
line.

## Project Structure

```
deck-harness/
├── verify_deck.py          # existing: deck-file batch verification
├── verify_card.py          # NEW: single-card lookup + rich table
├── tests/
│   ├── test_verify_deck.py # existing
│   └── test_verify_card.py # NEW
```

No new top-level dependency, no new package layout. `verify_card.py` stays a
flat script like `verify_deck.py`, per repo convention ("Match the style and
structure of surrounding code before proposing a new pattern").

## Code Style

Follow `docs/python-style.md` (Zen of Python, ruff-enforced: `E`, `F`, `W`,
`I`, `UP`, 100-char lines, Python 3.11 target).

Layer the script the same way `verify_deck.py` does:

1. **Check** — `fetch_card(name)`: hits `SCRYFALL_NAMED?exact=<name>`, returns
   `(found: bool, data: dict)` where `data` is the full card JSON on success or
   `{"details": "..."}`-shaped error info on 404. Reuses the same request
   pattern, `USER_AGENT`, and 429 exponential-backoff-up-to-4-attempts logic as
   `verify_deck.check_card` — copy the retry loop rather than importing across
   scripts, since these are two independent CLI entry points and the repo has
   no shared `lib/` module yet. Introducing one now for ~15 lines of retry
   logic would be exactly the "gratuitous abstraction" CLAUDE.md warns against;
   if a third script needs the same retry logic later, that's the trigger to
   extract it.
2. **Format** — `render_card_table(data)`: pure function, card dict in,
   formatted `str` out. Testable without any I/O or terminal.
3. **Report** — `main()`: argparse, calls fetch → format → print, returns exit
   code.

No third-party table/rich-text library (`rich`, `tabulate`) — stdlib
`str.ljust`/f-strings are sufficient for a fixed 7-row table and keep the
runtime dependency-free, consistent with `verify_deck.py`'s stdlib-only
constraint stated in `CLAUDE.md`.

## Testing Strategy

Same approach as `tests/test_verify_deck.py`: pytest, `monkeypatch` on
`urllib.request.urlopen` and `time.sleep`, no HTTP-mocking library. Target
100% coverage (`fail_under = 100` already set repo-wide in `pyproject.toml`
applies to `verify_card.py` too — no per-file exemption).

Cases to cover:

- Found: normal single-faced card (all fields present) → table renders all 7 rows.
- Found: double-faced card (`mana_cost`/`oracle_text` empty at top level,
  present under `card_faces[0]`) → fallback path exercised.
- Found: `prices.usd` is `null` → price row shows `n/a`.
- Not found (404): prints the ❌ message with Scryfall's suggestion detail.
- Rate limited (429 → retries → still 429 after 4 attempts): same backoff
  contract as `verify_deck.check_card`.
- Other HTTP error (e.g. 500): generic `HTTP <code>` failure path.
- Network error (`URLError`): generic network-error failure path.
- `main()` exit codes: 0 on found, 1 on not-found/error.

## Boundaries

**Always do:**
- Respect Scryfall's rate-limit etiquette: no request without the existing
  100ms `REQUEST_DELAY` convention isn't applicable here (single request per
  invocation), but the 429 exponential-backoff retry (same as
  `verify_deck.py`) is mandatory — never spin-retry without backoff.
- Send the same descriptive `User-Agent` header `verify_deck.py` uses.
- Keep the script stdlib-only at runtime (dev-only tooling — ruff, pytest —
  is the sole existing exception, per `CLAUDE.md`).
- Run `make be.lint` and `make be.test` after every change; both must exit 0
  before the work is reported done.

**Ask first about:**
- Any new runtime dependency (e.g. if a future request wants real ANSI-colored
  mana symbols via a library like `rich`).
- Adding flags/batch mode beyond the single-card v1 scope described here.
- Adding this script as a new `make` target or CI step (out of scope for this
  spec; ask before touching `.github/workflows/pull-request.yml` or
  `.make/backend.mk`).

**Never do:**
- Never hammer Scryfall: no polling loops, no concurrent requests, no retry
  without exponential backoff.
- Never introduce a shared module/package layout to "DRY up" the two scripts
  in this first pass — that's a call for the user to make later, not an
  agent-initiated refactor.
- Never drop below 100% test coverage on the new file.
