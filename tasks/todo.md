# Todo: Single-Card Scryfall Verification CLI

## Task 1: `fetch_card(name)` — exact-match lookup

**Description:** In new `verify_card.py`, add `fetch_card(name)` mirroring
`verify_deck.check_card`'s request/retry structure but returning the full
card JSON on success (not just name+bool). Query `SCRYFALL_NAMED?exact=<name>`,
same `USER_AGENT` header. Returns `(found: bool, data: dict)`:
- 200 → `(True, <full card dict>)`
- 404 → `(False, {"details": <scryfall detail or "not found">})`
- 429 → exponential backoff (`2**attempt`, up to 4 attempts), then
  `(False, {"details": "rate limited (HTTP 429)"})` if still failing
- other HTTPError → `(False, {"details": f"HTTP {code}"})`
- URLError → `(False, {"details": f"network error: {reason}"})`

**Acceptance criteria:**
- [x] `fetch_card("Sol Ring")`-style success returns `(True, dict)` with the
      real Scryfall fields intact
- [x] 404 returns `(False, {"details": ...})` using Scryfall's own detail text
- [x] 429 retries with backoff up to 4 attempts before giving up
- [x] Other HTTP errors and network errors return descriptive `(False, ...)`

**Verification:**
- [x] `make be.test` — new tests for all 5 paths above pass
- [x] 100% line/branch coverage of `fetch_card`

**Dependencies:** None

**Files likely touched:**
- `verify_card.py` (new)
- `tests/test_verify_card.py` (new)

**Estimated scope:** S

---

## Task 2: `render_card_table(data)` — pure formatting function

**Description:** Pure function, card dict in, formatted multi-line `str` out.
Renders the 7-row emoji table per SPEC.md (🃏 Name, 💠 Mana Cost, 📜 Type,
⭐ Rarity, 📦 Set, 📝 Text, 💵 Price USD). Falls back to `card_faces[0]` for
`mana_cost`/`oracle_text` when absent at top level (double-faced cards).
Renders `n/a` when `prices.usd` is `null`.

**Acceptance criteria:**
- [x] Single-faced card dict → all 7 rows render with correct values
- [x] Double-faced card dict (top-level `mana_cost`/`oracle_text` missing,
      present under `card_faces[0]`) → fallback values render correctly
- [x] `prices.usd is None` → Price row renders `n/a`
- [x] Output is a table (bordered/aligned), not a bare key: value dump

**Verification:**
- [x] `make be.test` — tests assert row content and table structure
- [x] 100% coverage of `render_card_table`, including the fallback branch

**Dependencies:** None (pure function, no fetch needed to test)

**Files likely touched:**
- `verify_card.py`
- `tests/test_verify_card.py`

**Estimated scope:** S

---

## Task 3: `render_not_found(name, detail)` — pure formatting function

**Description:** Pure function producing the ❌ not-found message per
SPEC.md, embedding the searched name and Scryfall's suggestion/detail text.

**Acceptance criteria:**
- [x] Output clearly states the card was not found (visually distinct — not
      a table row)
- [x] Output includes the `detail` string passed in (e.g. Scryfall's
      "did you mean" suggestion)

**Verification:**
- [x] `make be.test` — asserts message contains both name and detail
- [x] 100% coverage of `render_not_found`

**Dependencies:** None

**Files likely touched:**
- `verify_card.py`
- `tests/test_verify_card.py`

**Estimated scope:** XS

---

## Task 4: `main()` — argparse wiring and exit codes

**Description:** Add `main()`: one positional `name` arg, calls `fetch_card`,
dispatches to `render_card_table` or `render_not_found`, prints result,
returns `0` (found) or `1` (not found/error). Add
`if __name__ == "__main__": sys.exit(main())` guarded with
`# pragma: no cover`, matching `verify_deck.py`.

**Acceptance criteria:**
- [x] Running with a found card prints the table and exits 0
- [x] Running with a not-found card prints the ❌ message and exits 1
- [x] Running with an HTTP/network error prints an error and exits 1

**Verification:**
- [x] `make be.test` — integration tests monkeypatch `urllib.request.urlopen`
      and assert stdout (via `capsys`) + return code for each path
- [x] `make be.test` shows 100% coverage for `verify_card.py` overall
- [x] `make be.lint` exits 0
- [x] Manual: `python verify_card.py "Sol Ring"` and
      `python verify_card.py "Not A Real Card Xyz"` against live Scryfall

**Dependencies:** Tasks 1, 2, 3

**Files likely touched:**
- `verify_card.py`
- `tests/test_verify_card.py`

**Estimated scope:** S

---

## Task 5: Update `CLAUDE.md` docs and archive SPEC.md

**Description:** Add `verify_card.py` and `tests/test_verify_card.py` to the
Codebase Map, and document the fetch/format/report layering for
`verify_card.py` in the Architecture section (parallel to the existing
`verify_deck.py` breakdown), per this repo's CLAUDE.md rule that architecture
changes update CLAUDE.md. Then archive `SPEC.md` (root) to
`docs/specs/verify-card-cli.md` — repo root is for a spec in flight, not a
permanent record once the feature lands; `docs/` is where decisions/specs live
long-term (matches the `docs/ideas/testing-framework.md` precedent).

**Acceptance criteria:**
- [x] Codebase Map lists `verify_card.py` and its test file
- [x] Architecture section explains `fetch_card` / `render_card_table` /
      `render_not_found` / `main` and notes the intentional retry-logic
      duplication vs. `verify_deck.py` (and why, per SPEC.md)
- [x] `SPEC.md` moved (`git mv`) to `docs/specs/verify-card-cli.md`, root
      `SPEC.md` no longer exists

**Verification:**
- [x] Manual read-through: a new agent could locate and understand
      `verify_card.py` from CLAUDE.md alone
- [x] `ls SPEC.md` fails (not found); `ls docs/specs/verify-card-cli.md` succeeds

**Dependencies:** Task 4

**Files likely touched:**
- `CLAUDE.md`
- `SPEC.md` → `docs/specs/verify-card-cli.md` (moved)

**Estimated scope:** XS
