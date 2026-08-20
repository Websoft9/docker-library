.PHONY: help opencode install libs cli

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
	$(VENV_BIN)/pip install -e cli/
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
