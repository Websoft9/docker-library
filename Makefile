.PHONY: help opencode install libs cli remote test test-cli test-build test-skills contentful-create app-deploy app-down appstore-sync appstore-preview appstore-deploy app-tests

ifeq ($(OS),Windows_NT)
PYTHON ?= py
VENV_BIN := .venv/Scripts
VENV_ACTIVATE := .venv/Scripts/activate
else
PYTHON ?= python3
VENV_BIN := .venv/bin
VENV_ACTIVATE := .venv/bin/activate
endif

help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "; c="\033[1;36m"; g="\033[1;32m"; d="\033[2m"; r="\033[0m"} { if (NR==1) printf "\n  %s%s make targets%s\n\n  %s%s%s: %s<target>%s\n\n", c, "docker-library", r, d, "Usage", r, g, r } { printf "  %s%-16s%s %s\n", g, "make " $$1, r, $$2 } END { printf "\n" }'

opencode: ## start opencode with proxy disabled
	@echo "Starting opencode (proxy disabled)..."
	@unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy; \
	no_proxy="*" NO_PROXY="*" opencode

install: ## create .venv and install the libs CLI
	$(PYTHON) -m venv .venv
	$(VENV_BIN)/pip install -e 'cli/[test]'
	@proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
	if [ -n "$$proxy" ]; then \
		printf '%s' "$$proxy" > cli/proxy.conf; \
		echo "saved proxy: $$proxy"; \
	fi

libs: ## run one libs command, e.g. make libs ARGS="scan --app wordpress --json"
	@proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
	if [ -n "$$proxy" ]; then export https_proxy="$$proxy" http_proxy="$$proxy" all_proxy="$$proxy" no_proxy= NO_PROXY=; fi; \
	$(VENV_BIN)/libs $(ARGS)

cli: ## enter an activated shell for libs
	@echo "Entering a shell with the libs CLI activated. Type 'exit' to leave."
	@exec bash -c 'source $(VENV_ACTIVATE); \
		proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
		if [ -n "$$proxy" ]; then \
			printf '%s' "$$proxy" > cli/proxy.conf; \
			export https_proxy="$$proxy" http_proxy="$$proxy" all_proxy="$$proxy" no_proxy= NO_PROXY=; \
			echo "using proxy: $$proxy"; \
		else echo "no proxy detected"; fi; \
		libs -h; exec bash'

remote: ## interactively write .secrets/remote.env for remote-aware commands
	@mkdir -p .secrets
	@bash -lc 'set -e; \
	  current_target="$${TARGET:-remote}"; \
	  current_host="$${SSH_HOST:-}"; \
	  current_user="$${SSH_USER:-root}"; \
	  current_secret="$${SSH_SECRET_PATH:-.secrets/ssh/default.pem}"; \
	  current_path="$${DEPLOY_ROOT:-/opt/websoft9-test/apps}"; \
	  if [ -f .secrets/remote.env ]; then source .secrets/remote.env; \
	    current_target="$${TARGET:-$$current_target}"; \
	    current_host="$${SSH_HOST:-$$current_host}"; \
	    current_user="$${SSH_USER:-$$current_user}"; \
	    current_secret="$${SSH_SECRET_PATH:-$$current_secret}"; \
	    current_path="$${DEPLOY_ROOT:-$$current_path}"; \
	  fi; \
	  read -r -p "TARGET [$$current_target]: " input_target; input_target="$${input_target:-$$current_target}"; \
	  read -r -p "SSH_HOST [$$current_host]: " input_host; input_host="$${input_host:-$$current_host}"; \
	  read -r -p "SSH_USER [$$current_user]: " input_user; input_user="$${input_user:-$$current_user}"; \
	  read -r -p "SSH_SECRET_PATH [$$current_secret]: " input_secret; input_secret="$${input_secret:-$$current_secret}"; \
	  read -r -p "DEPLOY_ROOT [$$current_path]: " input_path; input_path="$${input_path:-$$current_path}"; \
	  printf "TARGET=%s\nSSH_HOST=%s\nSSH_USER=%s\nSSH_SECRET_PATH=%s\nDEPLOY_ROOT=%s\n" \
	    "$$input_target" "$$input_host" "$$input_user" "$$input_secret" "$$input_path" > .secrets/remote.env; \
	  chmod 600 .secrets/remote.env; \
	  echo "wrote .secrets/remote.env"'

test-cli: ## run cli unit and contract tests
	$(VENV_BIN)/python -m pytest cli/tests -q

test-build: ## run build pipeline smoke tests
	$(VENV_BIN)/python -m pytest tests/build -q

test-skills: ## run skills asset and workflow tests
	$(VENV_BIN)/python -m pytest tests/skills -q

contentful-create: ## preview or create a Contentful product entry, e.g. make contentful-create ARGS="--app ffmpeg --apply"
	$(VENV_BIN)/libs contentful-create $(ARGS)

app-deploy: ## run docker compose deploy/teardown for one app (localhost by default, remote-aware via .secrets/remote.env)
	$(VENV_BIN)/libs app-deploy $(ARGS)

app-down: ## tear one app down with docker compose down -v (localhost by default, remote-aware via .secrets/remote.env)
	$(VENV_BIN)/libs app-down $(ARGS)

appstore-sync: ## sync one app into the remote websoft9 appstore JSON preview and app directory
	$(VENV_BIN)/libs appstore-sync $(ARGS)

appstore-preview: ## deprecated alias of make appstore-sync
	$(VENV_BIN)/libs appstore-preview $(ARGS)

appstore-deploy: ## deploy one app into a websoft9 container appstore (not implemented yet; pending the websoft9 container CLI)
	$(VENV_BIN)/libs appstore-deploy $(ARGS)

app-tests: ## run app functional checks declared in apps/<app>/tests/cases.yml (localhost by default, remote-aware via .secrets/remote.env)
	$(VENV_BIN)/libs app-tests $(ARGS)

test: ## run the full repo machine-system test suite
	$(MAKE) --no-print-directory test-cli
	$(MAKE) --no-print-directory test-build
	$(MAKE) --no-print-directory test-skills
