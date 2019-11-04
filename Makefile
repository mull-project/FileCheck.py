# HELP ########################################################################

.PHONY: help
help: all
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

.PHONY: test-lit
FILECHECK_EXEC=$(PWD)/src/FileCheck.py
test-lit: ## Run LIT integration tests
	cd tests/integration && make clean
	CURRENT_DIR=$(PWD) \
		FILECHECK_EXEC=$(FILECHECK_EXEC) \
		PATH=$(PWD)/tests/integration/tools/FileCheck:$(PWD)/tests/integration/tools:$$PATH \
		lit \
		-vv $(PWD)/tests/integration
