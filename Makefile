SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

export VERSION := $(shell poetry version -s)

.PHONY: help
help: ## Print this help message
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: init
init: ## Locally install all dev dependencies
	poetry install --without playbook
	pnpm install

.PHONY: init-playbook
init-playbook: ## Locally install all playbook dev dependencies
	poetry install

.PHONY: clean
clean: ## clean project
	rm -fr build/ .pytest_cache/ .mypy_cache/
	-rm -rf node_modules

.PHONY: audit
audit: ## Audit project dependencies
	poetry export --without-hashes -f requirements.txt | poetry run safety check --full-report --stdin \
		--ignore 44715 --ignore 44716 --ignore 44717 --ignore 51668 # (https://github.com/numpy/numpy/issues/19038)
	pnpm audit --production

.PHONY: check-format
check-format: ## Check code formatting
	poetry run black --check .
	npx prettier --check 'src/**/*.{js,ts,tsx,json,yaml,css}'

.PHONY: format
format: ## Fix code formatting
	poetry run black .
	npx prettier --write 'src/**/*.{js,ts,tsx,json,yaml,css}'

.PHONY: typecheck
typecheck: ## Typecheck all source files
	poetry run mypy -p renumics.spotlight
	poetry run mypy -p renumics.spotlight_plugins.core
	poetry run mypy scripts
	pnpm run typecheck

.PHONY: lint
lint: ## Lint all source files
	poetry run pylint renumics tests ui_tests scripts/*.py
	pnpm run lint

TABLE_FILE ?= "data/tables/tallymarks-small.h5"
.PHONY: dev
dev: ## Start dev setup
	SPOTLIGHT_TABLE_FILE=$(TABLE_FILE) SPOTLIGHT_DEV=true poetry run spotlight

.PHONY: datasets
datasets: ## Build datasets (only needed for UI tests)
	mkdir -p build/datasets/
	poetry run python ./scripts/generate_test_csv.py -o build/datasets/
	poetry run python ./scripts/generate_demo_test_data.py -o build/datasets/
	poetry run python ./scripts/generate_performance_test_data.py -o build/datasets/

.PHONY: all-datasets
all-datasets: ## Build all datasets
all-datasets: datasets
	mkdir -p build/datasets/
	poetry run python ./scripts/generate_multimodal_test_data.py -o build/datasets/
	poetry run python ./scripts/generate_demo_test_data_ultra.py -o build/datasets/

.PHONY: build
build: ## Build package
build: build-frontend build-wheel

.PHONY: build-frontend
build-frontend: ## Build react frontend
	pnpm run build

.PHONY: build-wheel
build-wheel: ## Build installable python package
	[ -d "build/frontend" ] || (echo "Frontend directory missing! Build frontend first."; exit 1)
	function onexit {
		# remove local dist directory
		rm -rf dist || true
		# reset symlink for frontend
		rm -rf renumics/spotlight/backend/statics
		ln -nsf ../../../build/frontend renumics/spotlight/backend/statics
	}
	trap onexit EXIT
	rm renumics/spotlight/backend/statics
	cp -Tr build/frontend renumics/spotlight/backend/statics
	poetry build -f wheel
	mkdir -p build/dist/
	mv dist/*.whl build/dist/

.PHONY: check-wheel
check-wheel: ## Check wheel content
	poetry run check-wheel-contents build/dist/renumics_spotlight*

.PHONY: unit-test
unit-test: ## Execute tests
	poetry run pytest --doctest-modules --ignore=frontend --ignore=dev
	pnpm run test

.PHONY: api-test
api-test: ## Execute API tests
	function teardown {
		while kill -INT %% 2>/dev/null; do sleep 0; done  # kill all child processes
	}
	trap teardown EXIT
	PORT="5005"
	poetry run spotlight --host 127.0.0.1 --port $$PORT --no-browser data/tables/tallymarks-small.h5 &
	export BACKEND_BASE_URL="http://127.0.0.1:$${PORT}"
	wget -t20 -w0.5 --retry-connrefused --delete-after "$$BACKEND_BASE_URL"
	sleep 1
	pnpm run api-test

.PHONY: .ui-test-chrome
.ui-test-chrome:
	poetry run pytest -s --backendBaseUrl=$$BACKEND_BASE_URL --frontendBaseUrl=$$FRONTEND_BASE_URL $${CI:+--headless} ui_tests/

.PHONY: .ui-test-firefox
.ui-test-firefox:
	poetry run pytest -s -m "not skip_firefox" --backendBaseUrl=$$BACKEND_BASE_URL --frontendBaseUrl=$$FRONTEND_BASE_URL $${CI:+--headless} --browser firefox ui_tests/

.PHONY: ui-test-%
ui-test-%:
	function teardown {
		while kill -INT %% 2>/dev/null; do sleep 0; done  # kill all child processes
	}
	trap teardown EXIT
	PORT="5005"
	poetry run spotlight --host 127.0.0.1 --port $$PORT --no-browser . &
	export BACKEND_BASE_URL="http://127.0.0.1:$${PORT}"
	export FRONTEND_BASE_URL="http://127.0.0.1:$${PORT}"
	wget -t20 -w0.5 --retry-connrefused --delete-after "$$BACKEND_BASE_URL"
	sleep 1
	$(MAKE) .$@

.PHONY: test-spotlight-start
test-spotlight-start: ## Test Spotlight start (Spotlight should be installed)
	function teardown {
		while kill -INT %% 2>/dev/null; do sleep 0; done  # kill all child processes
	}
	trap teardown EXIT
	PORT="5005"
	spotlight --host 127.0.0.1 --port $$PORT --no-browser data/tables/tallymarks-small.h5 &
	URL="http://127.0.0.1:$${PORT}"
	wget -t20 -w0.5 --retry-connrefused --delete-after $$URL
	sleep 0.5
	GENERATION_ID=$$(wget -qO- "$${URL}/api/table/" | jq ".generation_id")
	wget --delete-after "$${URL}/api/table/number/42?generation_id=$${GENERATION_ID}"

.PHONY: test-spotlight-notebook-start
test-spotlight-notebook-start: ## Test Spotlight Notebook start (Spotlight should be installed)
	function teardown {
		rm -f output.log
	}
	trap teardown EXIT
	# kill -INT (s. start-spotlight-test) somehow does not work in CI, so we use timeout.
	timeout 20 spotlight-notebook -y --no-browser |& tee output.log &
	GREP_PATTERN='http://127.0.0.1:\S*'
	for i in {1..20}; do sleep 0.5; grep -qom1 $$GREP_PATTERN output.log && break; done
	wget -w1 --delete-after "$$(grep -om1 $$GREP_PATTERN output.log)"

.PHONY: docs
docs: ## Generate API docs
	rm -rf build/docs/api
	poetry run pdoc --template-dir docs/templates -o build/docs/api renumics.spotlight
	DOCS_WHITELIST=$$(sed -z 's/\n/|/g' docs/whitelist.txt)
	find build/docs/api/renumics/spotlight -type f -regextype egrep -not \
		-regex "build/docs/api/renumics/spotlight/($$DOCS_WHITELIST)" -delete
	find build/docs/api/renumics/spotlight -type d -empty -delete

DOCS_REPOSITORY ?= "../spotlight-docs"
.PHONY: dist-docs
dist-docs: ## Copy API docs to docs repository
dist-docs: docs
	[ -d "$(DOCS_REPOSITORY)" ] || (echo "Docs repository not found. Clone it to $(DOCS_REPOSITORY) or set its path to the DOCS_REPOSITORY variable."; exit 1)
	rsync -a --delete build/docs/api/renumics/spotlight/ "$(DOCS_REPOSITORY)/docs/api/spotlight"

AZURE_FOLDER_URL ?= "https://spotlightpublic.blob.core.windows.net/github-public/Renumics/spotlight-temp"
.PHONY: old-screenshots
old-screenshots: ## Generate the API spec and migrations
	TARGET_FOLDER="build/ui_tests/old-screenshots"
	rm -rf "$$TARGET_FOLDER"
	git fetch --all || true
	BRANCH="$$(git rev-parse --abbrev-ref HEAD)"
	COMMIT_SHA="$$([ "$$BRANCH" = "main" ] && git rev-parse main~ || git rev-parse main)"
	mkdir -p "$$TARGET_FOLDER"
	cd "$$TARGET_FOLDER"
	curl -fLO "${AZURE_FOLDER_URL}/$${COMMIT_SHA}/screenshots/gui-chrome.png" || true
	curl -fLO "${AZURE_FOLDER_URL}/$${COMMIT_SHA}/screenshots/gui-firefox.png" || true

.PHONY: api-client
api-client: ## Generate API Spec and CLient
	rm -rf /tmp/spotlight-api-client
	mkdir -p /tmp/spotlight-api-client
	poetry run python ./scripts/generate_api_spec.py -o /tmp/spotlight-api-spec.json
	npx @openapitools/openapi-generator-cli generate -g typescript-fetch \
		-i /tmp/spotlight-api-spec.json -o /tmp/spotlight-api-client
	# Fix generated code for multiple! file upload.
	# This is supported by oai 3 but openapi-generator does not support it (yet).
	find /tmp/spotlight-api-client \
		-type f -exec sed -i -e "s/formData.append('mesh_files',.*$$/for (let meshFile of requestParameters.meshFiles) { formData.append('mesh_files', meshFile) }/g" {} \;
	# replace existing code
	rsync -a --delete /tmp/spotlight-api-client/ "./frontend/src/client"
	# auto format generated code
	npx prettier --write './frontend/src/client/**/*.{js,ts,tsx,json,yaml,css}'

.PHONY: notebook-theme
notebook-theme: ## Generate custom css for jupyter notebook
	poetry run python ./scripts/build_notebook_theme.py
