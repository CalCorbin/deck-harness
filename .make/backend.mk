# ============================================================================
# 🏗 Core Targets
# ---------------------------------------------------------------------------
# All repos should implement these targets:
# ├── base.mk
# │   └── be.lint              ## Run linter / static analysis
# ============================================================================

# -----------------------------------------------------------------------------
# [be.setup] - 🔧 Create venv and install dev dependencies
# -----------------------------------------------------------------------------
.PHONY: be.setup
be.setup: ## 🔧 Create venv and install dev dependencies
	@$(call PRINT_HEADER,yellow)
	@$(MAKE) styles.println.green TEXT="Setting up venv..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -r requirements-dev.txt --quiet
	@$(MAKE) styles.println.green TEXT="✓ Setup complete"
	@$(call PRINT_FOOTER,yellow)

# -----------------------------------------------------------------------------
# [be.lint] - 🧹 Run linter / static analysis
# -----------------------------------------------------------------------------
.PHONY: be.lint
be.lint: ## 🧹 Run ruff linter checks
	@$(call PRINT_HEADER,yellow)
	@$(MAKE) styles.println.green TEXT="Running Ruff"
	@$(MAKE) styles.println.green TEXT="🧹 Linting code..."
	$(RUFF) check .
	@$(call PRINT_FOOTER,yellow)

# -----------------------------------------------------------------------------
# [be.test] - 🧪 Run test suite with coverage
# -----------------------------------------------------------------------------
.PHONY: be.test
be.test: ## 🧪 Run pytest with 100% coverage gate
	@$(call PRINT_HEADER,yellow)
	@$(MAKE) styles.println.green TEXT="Running pytest"
	@$(MAKE) styles.println.green TEXT="🧪 Testing code..."
	$(PYTEST) --cov=verify_deck --cov-report=term-missing
	@$(call PRINT_FOOTER,yellow)
