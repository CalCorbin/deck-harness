# Testing Framework for deck-harness

## Problem Statement

How might we adopt a reliable testing framework for `verify_deck.py` that supports
TDD and 100% coverage, without abandoning the repo's stdlib-first dependency policy?

## Recommended Direction

**pytest**, using stdlib `unittest.mock` primitives via pytest's built-in `monkeypatch`
fixture — no separate HTTP-mocking library (`responses`, `httpretty`, VCR.py).

pytest wins over stdlib `unittest` because the answers point to frequent local TDD:
parametrize (for `LINE_RE` edge cases), fixtures (`capsys`, `monkeypatch`), and plain
`assert` all reduce friction for a tight write-test/run-test loop. This is a real
exception to "prefer stdlib" — not a default reach for pytest — justified by the TDD
usage pattern, not by pytest being nicer.

`monkeypatch` is preferred over a third HTTP-mocking dependency because
`check_card()`'s only I/O surface is `urllib.request.urlopen` and `time.sleep` — both
directly patchable without adding a library whose only job is mocking sockets that
verify_deck.py doesn't actually open at the test level (no real socket — it's a single
`urlopen` call to patch).

## Key Assumptions to Validate

- [ ] pytest's `monkeypatch` can cleanly patch `urllib.request.urlopen` at the
      `verify_deck` module level without a refactor of `check_card()` — validate with
      a first spike test before committing to the pattern repo-wide.
- [ ] `time.sleep` must be patched in the same test as `urlopen` for the 429-backoff
      path, or coverage tests take 7+ real seconds (1+2+4s across 3 retries) — validate
      by writing the 429 test first and timing it.
- [ ] 100% coverage is achievable without contorting `check_card()`'s control flow —
      validate once all three layers (parse/check/report) have tests; if a branch
      resists clean testing, that's a signal the branch itself needs a small refactor,
      not a coverage exemption.

## MVP Scope

**In:**
- `pytest` + `pytest-cov`, pinned in `requirements-dev.txt`
- `tests/test_verify_deck.py` covering:
  - `parse_deck()` — count/name parsing, `Nx` syntax, skipped headers/blanks, malformed lines
  - `check_card()` — 200 (found), 404 (not found), 429 (backoff → retry → give up), other HTTP errors, network errors — all via `monkeypatch`, zero real network calls
  - `main()` — exit codes (0 all found, 1 any missing, 1 empty deck), stdout via `capsys`
- `pyproject.toml` addition: `[tool.coverage.report] fail_under = 100`
- `Makefile`/`.make/backend.mk` target: `be.test` (mirrors existing `be.lint` pattern)
- CI: add `be.test` step to `.github/workflows/pull-request.yml`
- Doc updates: `CLAUDE.md` codebase map + architecture section, `docs/python-style.md`
  testing section (repo rule: new pattern needs docs before PR)

**Out:**
- `hypothesis` property-based testing — nice-to-have for `LINE_RE` fuzzing, not needed
  to hit 100% coverage on the current deck format
- HTTP-mocking libraries (`responses`, `VCR.py`) — `monkeypatch` on `urlopen` is
  sufficient for this script's single I/O call
- `tox`/multi-Python-version matrix — repo targets one Python version (3.11 per ruff config)
- Contract/integration tests against live Scryfall API — would reintroduce rate-limit
  flakiness into CI that the retry logic exists to handle, not test

## Not Doing (and Why)

- **Refactoring `check_card()` for dependency injection** — mocking `urlopen` directly
  via `monkeypatch` works fine at current complexity; injecting a `fetch` callable would
  be premature abstraction for a single call site.
- **VCR.py cassette-based contract tests** — validates against Scryfall's real schema,
  but adds cassette-maintenance burden disproportionate to a single-script tool. Revisit
  if Scryfall's API shape becomes a recurring source of bugs.
- **Testing `REQUEST_DELAY` timing precisely** — asserting `time.sleep(0.1)` was called
  is enough; asserting exact wall-clock delay is brittle and untestable in CI reliably.

## Open Questions

- Does `fail_under = 100` in CI block merges on any coverage dip, or just report? (Recommend: block — matches "0% coverage debt" the user asked for.)
- Should `be.test` run before or after `be.lint` in CI? (Recommend: lint first — fail fast on style before spending time on test collection.)
