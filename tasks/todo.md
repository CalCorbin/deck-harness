# Todo: Add Ruff Lint

## Task 1: Add `pyproject.toml` with ruff config

**Description:** Create `pyproject.toml` with a `[tool.ruff]` section. Set target Python version, line length, and rule selection.

**Acceptance criteria:**
- [ ] `pyproject.toml` exists at repo root
- [ ] `[tool.ruff]` section sets `target-version`, `line-length`, and `select`

**Verification:**
- [ ] `python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` exits 0 (Python 3.11+) or file parses without error

**Dependencies:** None

**Files likely touched:**
- `pyproject.toml` (new)

**Estimated scope:** XS

---

## Task 2: Add `requirements-dev.txt` pinning ruff

**Description:** Add `requirements-dev.txt` with `ruff` pinned to a specific version so the venv install is reproducible.

**Acceptance criteria:**
- [ ] `requirements-dev.txt` exists with `ruff==<version>` line

**Verification:**
- [ ] `pip install -r requirements-dev.txt --dry-run` succeeds

**Dependencies:** None

**Files likely touched:**
- `requirements-dev.txt` (new)

**Estimated scope:** XS

---

## Task 3: Add `be.setup` make target

**Description:** Add `be.setup` to `backend.mk` that creates the venv and installs dev deps. Should be idempotent.

**Acceptance criteria:**
- [ ] `make be.setup` creates `.venv/` and installs ruff
- [ ] Running `make be.setup` a second time completes without error

**Verification:**
- [ ] `.venv/bin/ruff --version` succeeds after `make be.setup`

**Dependencies:** Task 2

**Files likely touched:**
- `.make/backend.mk`

**Estimated scope:** XS

---

## Task 4: Run end-to-end and fix lint issues

**Description:** Run `make be.setup && make be.lint`. Fix any ruff findings in `verify_deck.py`.

**Acceptance criteria:**
- [ ] `make be.lint` exits 0
- [ ] No ruff violations in `verify_deck.py`

**Verification:**
- [ ] `make be.lint` output shows no errors

**Dependencies:** Tasks 1, 2, 3

**Files likely touched:**
- `verify_deck.py` (fixes only if needed)

**Estimated scope:** XS
