# ============================================================================
# 🏗 Core Targets
# ---------------------------------------------------------------------------
# All repos should implement these targets:
# ├── base.mk
# │   └── help              ## Shows all targets from `.make/*.mk` files
# ============================================================================

# -----------------------------------------------------------------------------
# [help] - 📝 List all Makefile targets in colored tree format
# -----------------------------------------------------------------------------
.PHONY: help
help: ## 📝 List all Makefile targets in colored tree format
	@$(call PRINT_HEADER,yellow)
	@for mf in $(filter %.mk,$(MAKEFILE_LIST)); do \
		targets=$$(grep -E '^[[:space:]]*[a-zA-Z0-9_.%:-]+:.*?##' $$mf || true); \
		if [ ! -z "$$targets" ]; then \
			$(MAKE) styles.println.cyan TEXT="# ├── $$(basename $$mf)"; \
			maxlen=$$(echo "$$targets" | awk -F ':.*?##' '{print length($$1)}' | sort -nr | head -1); \
			count=$$(echo "$$targets" | wc -l); \
			i=1; \
			echo "$$targets" | while read t; do \
				name=$$(echo $$t | awk -F ':.*?##' '{print $$1}'); \
				desc=$$(echo $$t | awk -F ':.*?##' '{print $$2}'); \
				padded=$$(printf "%-*s" $$maxlen $$name); \
				if [ $$i -eq $$count ]; then \
					$(MAKE) styles.print.blue TEXT="# │   └── " ; \
					$(MAKE) styles.print.magenta TEXT="$$padded " ; \
					$(MAKE) styles.print.green TEXT="## $$desc" ; \
					echo ; \
				else \
					$(MAKE) styles.print.blue TEXT="# │   ├── " ; \
					$(MAKE) styles.print.magenta TEXT="$$padded " ; \
					$(MAKE) styles.print.green TEXT="## $$desc" ; \
					echo ; \
				fi; \
				i=$$((i+1)); \
			done; \
		fi; \
	done
	@$(call PRINT_FOOTER,yellow)