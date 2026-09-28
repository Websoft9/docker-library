.PHONY: help opencode opencode-clear install libs cli remote connector test test-cli test-build test-skills

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
	@printf '\n  \033[1;36mdocker-library make targets\033[0m\n\n'
	@printf '  \033[2mUsage\033[0m: \033[1;32mmake <target>\033[0m\n\n'
	@printf '  \033[1;35m▸ Dev\033[0m\n'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'opencode' 'start opencode with proxy disabled'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'opencode-clear' 'list opencode sessions, confirm, then delete them (ARGS: --all/--dry-run)'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'cli' 'enter an activated shell for libs'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'libs' 'run one libs command, e.g. make libs ARGS="scan --app wordpress --json"'
	@printf '\n  \033[1;35m▸ Testing & Quality\033[0m\n'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'test' 'run the full repo machine-system test suite'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'test-cli' 'run cli unit and contract tests'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'test-build' 'run build pipeline smoke tests'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'test-skills' 'run skills asset and workflow tests'
	@printf '\n  \033[1;35m▸ Config & Setup\033[0m\n'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'help' 'show this help'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'install' 'create .venv and install the libs CLI'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'remote' 'interactively write .secrets/remote.env for remote-aware commands'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'connector' 'interactively write .secrets/<provider>.env for external API tokens'
	@printf '\n'

opencode:
	@echo "Starting opencode (proxy disabled)..."
	@unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy; \
	no_proxy="*" NO_PROXY="*" opencode

opencode-clear:
	@$(PYTHON) build/opencode_delete.py $(ARGS)

install:
	$(PYTHON) -m venv .venv
	$(VENV_BIN)/pip install -e 'cli/[test]'
	@proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
	if [ -n "$$proxy" ]; then \
		printf '%s' "$$proxy" > cli/proxy.conf; \
		echo "saved proxy: $$proxy"; \
	fi

libs:
	@proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
	if [ -n "$$proxy" ]; then export https_proxy="$$proxy" http_proxy="$$proxy" all_proxy="$$proxy" no_proxy= NO_PROXY=; fi; \
	$(VENV_BIN)/libs $(ARGS)

cli:
	@echo "Entering a shell with the libs CLI activated. Type 'exit' to leave."
	@exec bash -c 'source $(VENV_ACTIVATE); \
		proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
		if [ -n "$$proxy" ]; then \
			printf '%s' "$$proxy" > cli/proxy.conf; \
			export https_proxy="$$proxy" http_proxy="$$proxy" all_proxy="$$proxy" no_proxy= NO_PROXY=; \
			echo "using proxy: $$proxy"; \
		else echo "no proxy detected"; fi; \
		libs -h; exec bash'

remote:
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

connector:
	@mkdir -p .secrets
	@bash -lc 'set -e; \
	  current_choice=1; \
	  if [ "${PROVIDER:-}" = "cloudflare" ] || [ "${PROVIDER:-}" = "2" ]; then current_choice=2; fi; \
	  if [ "${PROVIDER:-}" = "dockerhub" ] || [ "${PROVIDER:-}" = "3" ]; then current_choice=3; fi; \
	  if [ "${PROVIDER:-}" = "aliyun" ] || [ "${PROVIDER:-}" = "4" ]; then current_choice=4; fi; \
	  printf "Available providers:\n  1) contentful\n  2) cloudflare\n  3) dockerhub\n  4) aliyun (DNS)\n"; \
	  read -r -p "provider [$$current_choice]: " input_choice; input_choice="$${input_choice:-$$current_choice}"; \
	  case "$$input_choice" in \
	    1|contentful) provider="contentful"; file=".secrets/contentful.env"; key="CONTENTFUL_ACCESS_TOKEN" ;; \
	    2|cloudflare) provider="cloudflare"; file=".secrets/cloudflare.env"; key="CLOUDFLARE_API_TOKEN" ;; \
	    3|dockerhub) provider="dockerhub"; file=".secrets/dockerhub.env"; key="DOCKERHUB_TOKEN" ;; \
	    4|aliyun) provider="aliyun"; file=".secrets/aliyun.env"; key="ALIYUN_ACCESS_KEY_SECRET" ;; \
	    *) echo "unsupported provider selection: $$input_choice" >&2; exit 1 ;; \
	  esac; \
	  if [ -f "$$file" ]; then echo "updating $$file"; else echo "creating $$file"; fi; \
	  if [ "$$provider" = "aliyun" ]; then \
	    cur_id=""; cur_secret=""; cur_domain=""; \
	    if [ -f "$$file" ]; then \
	      cur_id="$$(grep -E '^ALIYUN_ACCESS_KEY_ID=' "$$file" | cut -d= -f2-)"; \
	      cur_secret="$$(grep -E '^ALIYUN_ACCESS_KEY_SECRET=' "$$file" | cut -d= -f2-)"; \
	      cur_domain="$$(grep -E '^ALIYUN_DNS_DOMAIN=' "$$file" | cut -d= -f2-)"; \
	    fi; \
	    read -r -p "ALIYUN_ACCESS_KEY_ID [$$cur_id]: " input_id; input_id="$${input_id:-$$cur_id}"; \
	    read -r -s -p "ALIYUN_ACCESS_KEY_SECRET [keep existing]: " input_secret; echo; input_secret="$${input_secret:-$$cur_secret}"; \
	    read -r -p "ALIYUN_DNS_DOMAIN (wildcard base, e.g. libs.websoft9.cn) [$$cur_domain]: " input_domain; input_domain="$${input_domain:-$$cur_domain}"; \
	    if [ -z "$$input_id" ] || [ -z "$$input_secret" ]; then echo "access key id and secret are required" >&2; exit 1; fi; \
	    if [ -n "$$input_domain" ]; then \
	      printf "ALIYUN_ACCESS_KEY_ID=%s\nALIYUN_ACCESS_KEY_SECRET=%s\nALIYUN_DNS_DOMAIN=%s\n" "$$input_id" "$$input_secret" "$$input_domain" > "$$file"; \
	    else \
	      printf "ALIYUN_ACCESS_KEY_ID=%s\nALIYUN_ACCESS_KEY_SECRET=%s\n" "$$input_id" "$$input_secret" > "$$file"; \
	    fi; \
	  elif [ "$$provider" = "dockerhub" ]; then \
	    cur_user=""; cur_token=""; cur_org=""; \
	    if [ -f "$$file" ]; then \
	      cur_user="$$(grep -E '^DOCKERHUB_USERNAME=' "$$file" | cut -d= -f2-)"; \
	      cur_token="$$(grep -E '^DOCKERHUB_TOKEN=' "$$file" | cut -d= -f2-)"; \
	      cur_org="$$(grep -E '^DOCKERHUB_ORG=' "$$file" | cut -d= -f2-)"; \
	    fi; \
	    read -r -p "DOCKERHUB_USERNAME [$$cur_user]: " input_user; input_user="$${input_user:-$$cur_user}"; \
	    read -r -s -p "DOCKERHUB_TOKEN [keep existing]: " input_token; echo; input_token="$${input_token:-$$cur_token}"; \
	    read -r -p "DOCKERHUB_ORG (optional default push namespace) [$$cur_org]: " input_org; input_org="$${input_org:-$$cur_org}"; \
	    if [ -z "$$input_user" ] || [ -z "$$input_token" ]; then echo "username and token are required" >&2; exit 1; fi; \
	    if [ -n "$$input_org" ]; then \
	      printf "DOCKERHUB_USERNAME=%s\nDOCKERHUB_TOKEN=%s\nDOCKERHUB_ORG=%s\n" "$$input_user" "$$input_token" "$$input_org" > "$$file"; \
	    else \
	      printf "DOCKERHUB_USERNAME=%s\nDOCKERHUB_TOKEN=%s\n" "$$input_user" "$$input_token" > "$$file"; \
	    fi; \
	  else \
	    read -r -s -p "$$key: " input_token; echo; \
	    if [ -z "$$input_token" ]; then echo "empty token is not allowed" >&2; exit 1; fi; \
	    printf "%s=%s\n" "$$key" "$$input_token" > "$$file"; \
	  fi; \
	  chmod 600 "$$file"; \
	  echo "wrote $$file"'

test-cli:
	$(VENV_BIN)/python -m pytest cli/tests -q

test-build:
	$(VENV_BIN)/python -m pytest tests/build -q

test-skills:
	$(VENV_BIN)/python -m pytest tests/skills -q

test:
	$(MAKE) --no-print-directory test-cli
	$(MAKE) --no-print-directory test-build
	$(MAKE) --no-print-directory test-skills
