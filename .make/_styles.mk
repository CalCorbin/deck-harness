# ============================================================================
# ✨ _styles.mk - helpers to style terminal output
# ============================================================================

TERM ?= xterm-256color

red := $(shell printf '\033[0;31m')
green := $(shell printf '\033[0;32m')
yellow := $(shell printf '\033[0;33m')
blue := $(shell printf '\033[0;34m')
cyan := $(shell printf '\033[0;36m')
nc := $(shell printf '\033[0m')

RED := $(red)
GREEN := $(green)
YELLOW := $(yellow)
BLUE := $(blue)
CYAN := $(cyan)
NC := $(nc)

# -----------------------------------------------------------------------------
# [println.line*] print a horizontal separator line across terminal width
# -----------------------------------------------------------------------------
.PHONY: styles.println.line
styles.println.line: ## 🎨 Print a horizontal separator line (default color)
	@cols=$${COLUMNS:-$$(tput cols 2>/dev/null || echo 120)}; \
	printf "%s%*s%s\n" "$(NC)" "$$cols" '' '' | tr ' ' '-';

.PHONY: styles.println.line.%
styles.println.line.%: ## 🎨 Print a horizontal separator line in COLOR (e.g., .green)
	@cols=$${COLUMNS:-$$(tput cols 2>/dev/null || echo 120)}; \
	printf "%s%*s%s\n" "$($*)" "$$cols" '' '' | tr ' ' '-';

# -----------------------------------------------------------------------------
# [🎨styles.println*] - Print-Line style color output
# Usage:
#   make styles.println TEXT="Hello"
#   make styles.println.COLOR TEXT="Hello"
# -----------------------------------------------------------------------------
.PHONY: styles.println
styles.println: ## 🎨 Print text with newline (default color)
	@text="$(TEXT)"; \
	printf "%b%b%b\n" "$(NC)" "$$text" "$(NC)";

.PHONY: styles.println.%
styles.println.%: ## 🎨 Print text with newline in COLOR (e.g., .green)
	@text="$(TEXT)"; \
	printf "%b%b%b\n" "$($*)" "$$text" "$(NC)";

# -----------------------------------------------------------------------------
# [🎨styles.print*] - Printf style color output
# Usage:
#   make styles.print TEXT="Hello"
#   make styles.print.COLOR TEXT="Hello"
# -----------------------------------------------------------------------------
.PHONY: styles.print
styles.print: ## 🎨 Print text without newline (default color)
	@text="$(TEXT)"; \
	printf "%b%b%b" "$(NC)" "$$text" "$(NC)";

.PHONY: styles.print.%
styles.print.%: ## 🎨 Print text without newline in COLOR (e.g., .red)
	@text="$(TEXT)"; \
	printf "%b%b%b" "$($*)" "$$text" "$(NC)";

# -----------------------------------------------------------------------------
# [🎨styles.print.padding] - Print empty padding lines
# -----------------------------------------------------------------------------
.PHONY: styles.print.padding
styles.print.padding: ## 🎨 Print empty padding lines
	@printf "\n\n";

# ----------------------------------------------------------------------------
# [🖌 PRINT_HEADER] - Print a styled header block for a make target
# -----------------------------------------------------------------------------
define PRINT_HEADER
	@$(MAKE) styles.println.line.$(1)
	@$(MAKE) styles.println.$(1) TEXT="🖌  [Running]: 'make $@'"
	@$(MAKE) styles.println.line.$(1)
endef

# -----------------------------------------------------------------------------
# [🖌 PRINT_FOOTER] - Print a styled footer line for a make target
# -----------------------------------------------------------------------------
define PRINT_FOOTER
	@$(MAKE) styles.println.line.$(1)
endef