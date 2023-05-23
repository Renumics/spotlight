SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

export VERSION := $(shell poetry version -s)
export SKIP_PREFLIGHT_CHECK := true

.PHONY: help
help: ## Print this help message
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: init
init: ## locally install all (dev) typescript dependencies
	pnpm install

.PHONY: clean
clean: ## remove installed dependencies
	-rm -rf node_modules

.PHONY: audit
audit: ## check for vulnerabilities in production dependencies
	pnpm audit --production

.PHONY: check-format
check-format: ## Check code formatting
	npx prettier --check 'src/**/*.{js,ts,tsx,json,yaml,css}'
	poetry run black --check ui_tests

.PHONY: format
format: ## Fix code formatting
	npx prettier --write 'src/**/*.{js,ts,tsx,json,yaml,css}'
	poetry run black ui_tests

.PHONY: typecheck
typecheck: ## check type
	pnpm run typecheck
	PYTHONPATH=. poetry run mypy ui_tests

.PHONY: lint
lint: ## check code (and config) formatting
	pnpm run lint
	poetry run pylint ui_tests

.PHONY: build
build: ## build static gui
	pnpm run build

.PHONY: unit-test
unit-test: ## run npm tests in the project
	pnpm run test

.PHONY: api-test
api-test: ## run api tests
	pnpm run api-test

.PHONY: ui-test-chrome
ui-test-chrome: ## run visual regression tests on ui
	poetry run pytest -s --backendBaseUrl=$$BACKEND_BASE_URL --frontendBaseUrl=$$FRONTEND_BASE_URL $${CI:+--headless} ui_tests/

.PHONY: ui-test-firefox
ui-test-firefox: ## run visual regression tests on ui
	poetry run pytest -s -m "not skip_firefox" --backendBaseUrl=$$BACKEND_BASE_URL --frontendBaseUrl=$$FRONTEND_BASE_URL $${CI:+--headless} --browser firefox ui_tests/
