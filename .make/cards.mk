# ============================================================================
# 🃏 Card Targets
# ---------------------------------------------------------------------------
# ├── cards.mk
# │   └── card.verify          ## Verify a single card exists on Scryfall
# ============================================================================

# -----------------------------------------------------------------------------
# [card.verify] - 🔍 Verify a single card exists on Scryfall
# -----------------------------------------------------------------------------
.PHONY: card.verify
card.verify: ## 🔍 Verify a single card exists on Scryfall (usage: make card.verify NAME='Card Name')
	@$(call PRINT_HEADER,yellow)
	@if [ -z "$(NAME)" ]; then \
		$(MAKE) styles.println.red TEXT="Usage: make card.verify NAME='Card Name'"; \
		exit 1; \
	fi
	$(PYTHON) verify_card.py "$(NAME)"
	@$(call PRINT_FOOTER,yellow)
