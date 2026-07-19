# ============================================================================
# 🃏 Card Targets
# ---------------------------------------------------------------------------
# ├── cards.mk
# │   └── card.verify          ## Verify a single card exists on Scryfall
# ============================================================================

CARD_NAME := $(filter-out card.verify,$(MAKECMDGOALS))

# -----------------------------------------------------------------------------
# [card.verify] - 🔍 Verify a single card exists on Scryfall
# -----------------------------------------------------------------------------
.PHONY: card.verify
card.verify: ## 🔍 Verify a single card exists on Scryfall (usage: make card.verify 'Card Name')
	@$(call PRINT_HEADER,yellow)
	@if [ -z "$(CARD_NAME)" ]; then \
		$(MAKE) styles.println.red TEXT="Usage: make card.verify 'Card Name'"; \
		exit 1; \
	fi
	$(PYTHON) verify_card.py "$(CARD_NAME)"
	@$(call PRINT_FOOTER,yellow)

# The card name arrives as a second make goal (e.g. `make card.verify "Sol
# Ring"`), so it needs a no-op rule or make tries to build it as a target of
# its own. A goal quoted on the shell command line keeps its embedded spaces
# as one MAKECMDGOALS entry, and a make target name can only contain a space
# if that space is backslash-escaped in the rule — hence the $(subst) below.
_cm_empty :=
_cm_space := $(_cm_empty) $(_cm_empty)
ifneq (,$(filter card.verify,$(MAKECMDGOALS)))
$(eval $(subst $(_cm_space),\$(_cm_space),$(CARD_NAME)):;@:)
endif
