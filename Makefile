### HELP #######################################################################

.PHONY: help
help:
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

.PHONY: test-lit

ifdef REAL_ONLY
test-lit: test-lit-real ## Run tests against FileCheck C++ only (only when REAL_ONLY is provided).
	@echo "Have run real FileCheck C++ tests."
else
test-lit: test-lit-real test-lit-py ## Run tests against both FileCheck C++ and FileCheck.py.
	@echo "Have run both real FileCheck C++ and FileCheck.py tests."
endif

FILECHECK_PY_EXEC=$(PWD)/filecheck/FileCheck.py
test-lit-py: ## Run tests against FileCheck.py.
	@echo "--- Running integration tests against FileCheck.py ---"
	cd tests/integration && make clean

	CURRENT_DIR=$(PWD) \
		FILECHECK_EXEC=$(FILECHECK_PY_EXEC) \
		PATH=$(PWD)/tests/integration/tools/FileCheck:$(PWD)/tests/integration/tools:$$PATH \
		lit \
		-vv $(PWD)/tests/integration

test-lit-real: test-lit-real-8 test-lit-real-9 ## Run tests against FileCheck C++.

FILECHECK_REAL_8_EXEC=$(PWD)/tests/integration/tools/FileCheck/FileCheck-8.0.1
test-lit-real-8: ## Run tests against FileCheck
	@echo "--- Running integration tests against LLVM FileCheck 8.0.1 ---"
	cd tests/integration && make clean

	CURRENT_DIR=$(PWD) \
		REAL_ONLY=1 \
		FILECHECK_EXEC=$(FILECHECK_REAL_8_EXEC) \
		PATH=$(PWD)/tests/integration/tools/FileCheck:$(PWD)/tests/integration/tools:$$PATH \
		lit \
		-vv $(PWD)/tests/integration

FILECHECK_REAL_9_EXEC=$(PWD)/tests/integration/tools/FileCheck/FileCheck-9.0.1
test-lit-real-9: ## Run tests against FileCheck C++.
	@echo "--- Running integration tests against LLVM FileCheck 9.0.1 ---"
	cd tests/integration && make clean

	CURRENT_DIR=$(PWD) \
		REAL_ONLY=1 \
		FILECHECK_EXEC=$(FILECHECK_REAL_9_EXEC) \
		PATH=$(PWD)/tests/integration/tools/FileCheck:$(PWD)/tests/integration/tools:$$PATH \
		lit \
		-vv $(PWD)/tests/integration

# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
changelog: ## Generate changelog
	CHANGELOG_GITHUB_TOKEN=$(CHANGELOG_GITHUB_TOKEN) github_changelog_generator \
		--user stanislaw \
		--project FileCheck.py

