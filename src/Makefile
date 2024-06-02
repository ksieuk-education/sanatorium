include ../common_makefile.mk

PROJECT_FOLDERS = bin lib tests

.PHONY: ci-test
ci-test:
	@echo 'Running tests...'
	@$(PYTHON) -m pytest tests/unit
