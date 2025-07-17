PATCH_DIR := patches
BUILD_DIR := build

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Usage:"
	@echo "  make patch/<name>   - Clone, patch, and build the given repo"
	@echo ""
	@echo "  Example: make patch/hashicorp-vault"

# Pattern rule: "patch/NAME"
patch/%:
	@name=$* ; \
	repo=$$(echo $$name | sed 's|-|/|') ; \
	echo "🔧 Building and patching: $$repo" ; \
	rm -rf $(BUILD_DIR)/$$name ; \
	git clone --depth 1 --branch main https://github.com/$$repo $(BUILD_DIR)/$$repo ; \
	cp $(PATCH_DIR)/$$name.patch $(BUILD_DIR)/$$repo && cd $(BUILD_DIR)/$$repo && patch -p1 < $$name.patch ; \
	make

