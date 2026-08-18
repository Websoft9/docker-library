.PHONY: help opencode install libs cli

help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

opencode: ## start opencode with proxy disabled
	@echo "Starting opencode (proxy disabled)..."
	@unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy; \
	no_proxy="*" NO_PROXY="*" opencode

install: ## create .venv and install the libs CLI
	python3 -m venv .venv
	.venv/bin/pip install -e cli/

libs: ## run one libs command, e.g. make libs ARGS="validate --app wordpress"
	@.venv/bin/libs $(ARGS)

cli: ## enter an activated shell for libs
	@echo "Entering a shell with the libs CLI activated. Type 'exit' to leave."
	@exec bash -c 'source .venv/bin/activate && libs -h && exec bash'
