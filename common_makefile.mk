PENV = .venv
NENV = ../../node_modules

PYTHON = $(PENV)/bin/python
PYRIGHT = $(NENV)/.bin/pyright
PRETTIER = $(NENV)/.bin/prettier
RUFF = $(PENV)/bin/ruff
TOML_SORT = $(PENV)/bin/toml-sort

VERSION = $(shell poetry version --short)

.PHONY: init
init:
	@echo 'Installing python dependencies...'
	@poetry install

.PHONY: lint
lint:
	@echo 'Running poetry checks...'
	@poetry check

	@echo 'Running black checks...'
	@$(PYTHON) -m black --check .

	@echo 'Running isort checks...'
	@$(PYTHON) -m isort --check .

	@echo 'Running toml-sort checks...'
	@$(TOML_SORT) --check poetry.toml pyproject.toml
	@echo ''

	@echo 'Running pylint checks...'
	@$(PYTHON) -m pylint .

	@echo 'Running pyright checks...'
	@$(PYRIGHT)

.PHONY: lint-fix
lint-fix:
	@echo 'Running poetry autofixes...'
	@poetry check
	@poetry lock --no-update

	@echo 'Running black autofixes...'
	@$(PYTHON) -m black --safe .
	@echo ''

	@echo 'Running isort autofixes...'
	@$(PYTHON) -m isort --atomic .
	@echo ''

	@echo 'Running toml-sort autofixes...'
	@$(TOML_SORT) --in-place poetry.toml pyproject.toml
	@echo ''

	@echo 'Running sort-all autofixes...'
	@find $(PROJECT_FOLDERS) -name '*.py' -type f -exec $(PYTHON) -m sort_all '{}' \;

	@echo 'Running pyupgrade autofixes...'
	@find $(PROJECT_FOLDERS) -name '*.py' -type f -exec $(PYTHON) -m pyupgrade --py311-plus --keep-runtime-typing '{}' \;

	@echo 'Running pylint checks...'
	@$(PYTHON) -m pylint .

	@echo 'Running prettier auto-fixes...'
	@$(PRETTIER) . "!.venv/**" --write

	@echo 'Running pyright checks...'
	@$(PYRIGHT)

	@echo 'Running ruff checks...'
	@$(RUFF) .

.PHONY: test
test:
	@echo 'Running tests...'
	@$(PYTHON) -m pytest tests

.PHONY: clean
clean:
	@echo 'Cleaning python dependencies...'
	@rm -rf $(PENV)

	@echo 'Cleaning dist packages...'
	@rm -rf dist

	@echo 'Cleaning pytest cache...'
	@rm -rf .pytest_cache

.PHONY: dependencies-update
dependencies-update:
	@echo 'Updating python dependencies...'
	@poetry update


# CI-specific

.PHONY: ci-test
ci-test:
	@echo 'Running tests...'
	@$(PYTHON) -m pytest tests


.PHONY: ci-package-build
ci-package-build:
	@echo 'Building package...'
	@poetry build --no-interaction
