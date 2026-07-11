# ============================================================================
# ✨ _template.mk - template for new Makefile sections
# ============================================================================

# -----------------------------------------------------------------------------
# [📌example] - Example target to demonstrate Makefile structure
# -----------------------------------------------------------------------------
.PHONY: example
example: ## 👋 short description for help menu
	$(call PRINT_HEADER,yellow)
	@$(MAKE) styles.println.padding
	@$(MAKE) styles.println.green TEXT="👋 Hello from example!"
	@$(MAKE) styles.println.line
	$(call PRINT_FOOTER,yellow)

# -----------------------------------------------------------------------------
# [🏗example.fizzbuzz] - FizzBuzz style coding interview problem
# -----------------------------------------------------------------------------
.PHONY: example.fizzbuzz
example.foobar: ## 👋 FizzBuzz L33tc0d1ng pr0bl3m
	$(call PRINT_HEADER,yellow)
	@bash -c 'for i in {1..10}; do \
			output=""; \
			[ $$((i%3)) -eq 0 ] && output="Foo"; \
			[ $$((i%5)) -eq 0 ] && output="Bar"; \
			[ -z "$$output" ] && output=$$i; \
			echo "$$output"; \
		done'
	$(call PRINT_FOOTER,yellow)

