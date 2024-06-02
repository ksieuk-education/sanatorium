NENV = node_modules
PRETTIER = $(NENV)/.bin/prettier

SHELL = /bin/bash
.PHONY: init
init:
	@echo 'Installing node version...'
	@. $(HOME)/.nvm/nvm.sh && nvm install

	@echo 'Installing node dependencies...'
	@npm install

	@echo 'Installing husky pre-commit...'
	@npm run prepare-husky

.PHONY: lint
lint:
	@echo 'Running prettier checks...'
	@$(PRETTIER) --check .

.PHONY: lint-fix
lint-fix:
	@echo 'Running prettier auto-fixes...'
	@$(PRETTIER) --write .

.PHONY: test
test:
	@echo 'Running tests...'

.PHONY: clean
clean:
	@echo 'Cleaning up node dependencies...'
	@rm -rf $(NENV)

	@echo "Cleaning src/..."; \
	make -C src/ clean || exit 1; \

# Commands for every package

.PHONY: all-init
all-init:
	@echo "Initializing src/..."; \
	make -C src/ init || exit 1; \

.PHONY: all-lint
all-lint:
	@echo "Linting src/..."; \
	make -C src/ lint || exit 1; \

.PHONY: all-lint-fix
all-lint-fix:
	@echo "Fixing lint issues for src/..."; \
	make -C src/ lint-fix || exit 1; \

.PHONY: all-test
all-test:
	@echo "Testing src/..."; \
	make -C src/ test || exit 1; \

.PHONY: all-clean
all-clean:
	@echo "Cleaning src/..."; \
	make -C src/ clean || exit 1; \

.PHONY: all-dependencies-update
all-dependencies-update:
	@echo "Updating dependencies for src/..."; \
	make -C src/ dependencies-update || exit 1; \

# CI-specific

.PHONY: ci-init
ci-init:
	@echo 'Installing node dependencies...'
	@npm install
