.PHONY: help opencode opencode-clear install libs cli branch-update remote connector github-token install-git-hooks dns-bind dns-delete websoft9-upgrade create-aliyun-ecs build-ai-commands i18n-check i18n-update test test-cli test-build test-skills

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
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'branch-update' 'on a development branch: delete its remote, rebase onto latest origin/main, update local main (ARGS: --dry-run/--force)'
	@printf '\n  \033[1;35m▸ Server Ops\033[0m\n'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'dns-bind' 'point the wildcard record (*.<domain>) at the remote host or localhost (ARGS: --domain/--ip/--json)'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'dns-delete' 'delete the single wildcard record (*.<domain>) for the domain (ARGS: --domain/--json)'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'websoft9-upgrade' 'upgrade the Websoft9 platform container: set image tag, pull, recreate (ARGS: --tag/--target)'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'create-aliyun-ecs' 'create a spot Aliyun ECS instance from ci/cloud/aliyun-ecs.json (interactive instance type/disk/release; ARGS: --instance-type/--disk-size/--release-in)'
	@printf '\n  \033[1;35m▸ Testing & Quality\033[0m\n'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'test' 'run the full repo machine-system test suite'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'test-cli' 'run cli unit and contract tests'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'test-build' 'run build pipeline smoke tests'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'test-skills' 'run skills asset and workflow tests'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'build-ai-commands' 'generate opencode/copilot/codex command adapters from manifest'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'i18n-check' 'check translation.json for missing keys (ARGS: --strict, --app <app>)'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'i18n-update' 'add missing translation keys as ["", ""]'
	@printf '\n  \033[1;35m▸ Config & Setup\033[0m\n'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'help' 'show this help'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'install' 'create .venv and install the libs CLI'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'remote' 'interactively write .secrets/remote.env for remote-aware commands'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'connector' 'interactively write .secrets/<provider>.env for API tokens, DNS and cloud credentials'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'github-token' 'configure the GitHub MCP token for opencode'
	@printf '  \033[2mmake \033[0m\033[1;32m%-18s\033[0m %s\n' 'install-git-hooks' 'set core.hooksPath=.githooks and enable local quality hooks'
	@printf '\n'

opencode:
	@echo "Starting opencode (proxy disabled)..."
	@unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy; \
	no_proxy="*" NO_PROXY="*" opencode

opencode-clear:
	@$(PYTHON) ci/scripts/opencode_delete.py $(ARGS)

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

branch-update:
	@bash ci/scripts/branch_update.sh $(ARGS)

dns-bind:
	@proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
	if [ -n "$$proxy" ]; then export https_proxy="$$proxy" http_proxy="$$proxy" all_proxy="$$proxy" no_proxy= NO_PROXY=; fi; \
	$(VENV_BIN)/python -m libs.ops dns-bind $(ARGS)

dns-delete:
	@proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
	if [ -n "$$proxy" ]; then export https_proxy="$$proxy" http_proxy="$$proxy" all_proxy="$$proxy" no_proxy= NO_PROXY=; fi; \
	$(VENV_BIN)/python -m libs.ops dns-delete $(ARGS)

websoft9-upgrade:
	@proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
	if [ -n "$$proxy" ]; then export https_proxy="$$proxy" http_proxy="$$proxy" all_proxy="$$proxy" no_proxy= NO_PROXY=; fi; \
	$(VENV_BIN)/python -m libs.ops websoft9-upgrade $(ARGS)

create-aliyun-ecs:
	@proxy="$${https_proxy:-$${HTTPS_PROXY:-$${http_proxy:-$${HTTP_PROXY:-}}}}"; \
	if [ -n "$$proxy" ]; then export https_proxy="$$proxy" http_proxy="$$proxy" all_proxy="$$proxy" no_proxy= NO_PROXY=; fi; \
	$(VENV_BIN)/python -m libs.ops create-aliyun-ecs $(ARGS)

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

github-token:
	@$(PYTHON) ci/scripts/configure_github_mcp.py $(ARGS)

install-git-hooks:
	@git config core.hooksPath .githooks
	@chmod +x .githooks/pre-commit .githooks/pre-push
	@echo "configured git hooks path: .githooks"

build-ai-commands:
	@$(PYTHON) ci/scripts/build_ai_commands.py $(ARGS)

connector:
	@mkdir -p .secrets
	@bash -lc 'set -e; \
	  current_choice=1; \
	  if [ "$${PROVIDER:-}" = "cloudflare" ] || [ "$${PROVIDER:-}" = "2" ]; then current_choice=2; fi; \
	  if [ "$${PROVIDER:-}" = "dockerhub" ] || [ "$${PROVIDER:-}" = "3" ]; then current_choice=3; fi; \
	  if [ "$${PROVIDER:-}" = "dns" ] || [ "$${PROVIDER:-}" = "4" ]; then current_choice=4; fi; \
	  if [ "$${PROVIDER:-}" = "alibabacloud" ] || [ "$${PROVIDER:-}" = "5" ]; then current_choice=5; fi; \
	  if [ "$${PROVIDER:-}" = "aws" ] || [ "$${PROVIDER:-}" = "6" ]; then current_choice=6; fi; \
	  if [ "$${PROVIDER:-}" = "azure" ] || [ "$${PROVIDER:-}" = "7" ]; then current_choice=7; fi; \
	  printf "Available providers:\n  1) contentful\n  2) cloudflare\n  3) dockerhub\n  4) dns\n  5) alibabacloud\n  6) aws\n  7) azure\n"; \
	  read -r -p "provider [$$current_choice]: " input_choice; input_choice="$${input_choice:-$$current_choice}"; \
	  case "$$input_choice" in \
	    1|contentful) provider="contentful"; file=".secrets/contentful.env"; key="CONTENTFUL_ACCESS_TOKEN" ;; \
	    2|cloudflare) provider="cloudflare"; file=".secrets/cloudflare.env"; key="CLOUDFLARE_API_TOKEN" ;; \
	    3|dockerhub) provider="dockerhub"; file=".secrets/dockerhub.env"; key="DOCKERHUB_TOKEN" ;; \
	    4|dns) provider="dns"; file=".secrets/dns.env" ;; \
	    5|alibabacloud) provider="aliyun"; file=".secrets/aliyun.env" ;; \
	    6|aws) provider="aws"; file=".secrets/aws.env" ;; \
	    7|azure) provider="azure"; file=".secrets/azure.env" ;; \
	    *) echo "unsupported provider selection: $$input_choice" >&2; exit 1 ;; \
	  esac; \
	  if [ -f "$$file" ]; then echo "updating $$file"; else echo "creating $$file"; fi; \
	  if [ "$$provider" = "dns" ]; then \
	    cur_dns=""; cur_id=""; cur_secret=""; cur_domain=""; \
	    if [ -f "$$file" ]; then \
	      cur_dns="$$(grep -E '^DNS_PROVIDER=' "$$file" | cut -d= -f2-)"; \
	      cur_id="$$(grep -E '^DNS_KEY_ID=' "$$file" | cut -d= -f2-)"; \
	      cur_secret="$$(grep -E '^DNS_KEY_SECRET=' "$$file" | cut -d= -f2-)"; \
	      cur_domain="$$(grep -E '^DNS_DOMAIN=' "$$file" | cut -d= -f2-)"; \
	    fi; \
	    cur_dns="$${cur_dns:-aliyun}"; \
	    read -r -p "DNS_PROVIDER (e.g. aliyun) [$$cur_dns]: " input_dns; input_dns="$${input_dns:-$$cur_dns}"; \
	    read -r -p "DNS_KEY_ID [$$cur_id]: " input_id; input_id="$${input_id:-$$cur_id}"; \
	    read -r -s -p "DNS_KEY_SECRET [keep existing]: " input_secret; echo; input_secret="$${input_secret:-$$cur_secret}"; \
	    read -r -p "DNS_DOMAIN (wildcard base, e.g. libs.websoft9.cn) [$$cur_domain]: " input_domain; input_domain="$${input_domain:-$$cur_domain}"; \
	    if [ -z "$$input_dns" ] || [ -z "$$input_id" ] || [ -z "$$input_secret" ]; then echo "provider, key id and secret are required" >&2; exit 1; fi; \
	    if [ -n "$$input_domain" ]; then \
	      printf "DNS_PROVIDER=%s\nDNS_KEY_ID=%s\nDNS_KEY_SECRET=%s\nDNS_DOMAIN=%s\n" "$$input_dns" "$$input_id" "$$input_secret" "$$input_domain" > "$$file"; \
	    else \
	      printf "DNS_PROVIDER=%s\nDNS_KEY_ID=%s\nDNS_KEY_SECRET=%s\n" "$$input_dns" "$$input_id" "$$input_secret" > "$$file"; \
	    fi; \
	  elif [ "$$provider" = "aliyun" ]; then \
	    cur_id=""; cur_secret=""; cur_region=""; \
	    if [ -f "$$file" ]; then \
	      cur_id="$$(grep -E '^ALIYUN_ACCESS_KEY_ID=' "$$file" | cut -d= -f2-)"; \
	      cur_secret="$$(grep -E '^ALIYUN_ACCESS_KEY_SECRET=' "$$file" | cut -d= -f2-)"; \
	      cur_region="$$(grep -E '^ALIYUN_REGION=' "$$file" | cut -d= -f2-)"; \
	    fi; \
	    read -r -p "ALIYUN_ACCESS_KEY_ID [$$cur_id]: " input_id; input_id="$${input_id:-$$cur_id}"; \
	    read -r -s -p "ALIYUN_ACCESS_KEY_SECRET [keep existing]: " input_secret; echo; input_secret="$${input_secret:-$$cur_secret}"; \
	    read -r -p "ALIYUN_REGION (optional, e.g. cn-hongkong) [$$cur_region]: " input_region; input_region="$${input_region:-$$cur_region}"; \
	    if [ -z "$$input_id" ] || [ -z "$$input_secret" ]; then echo "access key id and secret are required" >&2; exit 1; fi; \
	    if [ -n "$$input_region" ]; then \
	      printf "ALIYUN_ACCESS_KEY_ID=%s\nALIYUN_ACCESS_KEY_SECRET=%s\nALIYUN_REGION=%s\n" "$$input_id" "$$input_secret" "$$input_region" > "$$file"; \
	    else \
	      printf "ALIYUN_ACCESS_KEY_ID=%s\nALIYUN_ACCESS_KEY_SECRET=%s\n" "$$input_id" "$$input_secret" > "$$file"; \
	    fi; \
	  elif [ "$$provider" = "aws" ]; then \
	    cur_id=""; cur_secret=""; cur_region=""; \
	    if [ -f "$$file" ]; then \
	      cur_id="$$(grep -E '^AWS_ACCESS_KEY_ID=' "$$file" | cut -d= -f2-)"; \
	      cur_secret="$$(grep -E '^AWS_SECRET_ACCESS_KEY=' "$$file" | cut -d= -f2-)"; \
	      cur_region="$$(grep -E '^AWS_REGION=' "$$file" | cut -d= -f2-)"; \
	    fi; \
	    read -r -p "AWS_ACCESS_KEY_ID [$$cur_id]: " input_id; input_id="$${input_id:-$$cur_id}"; \
	    read -r -s -p "AWS_SECRET_ACCESS_KEY [keep existing]: " input_secret; echo; input_secret="$${input_secret:-$$cur_secret}"; \
	    read -r -p "AWS_REGION (optional, e.g. us-east-1) [$$cur_region]: " input_region; input_region="$${input_region:-$$cur_region}"; \
	    if [ -z "$$input_id" ] || [ -z "$$input_secret" ]; then echo "access key id and secret are required" >&2; exit 1; fi; \
	    if [ -n "$$input_region" ]; then \
	      printf "AWS_ACCESS_KEY_ID=%s\nAWS_SECRET_ACCESS_KEY=%s\nAWS_REGION=%s\n" "$$input_id" "$$input_secret" "$$input_region" > "$$file"; \
	    else \
	      printf "AWS_ACCESS_KEY_ID=%s\nAWS_SECRET_ACCESS_KEY=%s\n" "$$input_id" "$$input_secret" > "$$file"; \
	    fi; \
	  elif [ "$$provider" = "azure" ]; then \
	    cur_sub=""; cur_tenant=""; cur_client=""; cur_secret=""; \
	    if [ -f "$$file" ]; then \
	      cur_sub="$$(grep -E '^AZURE_SUBSCRIPTION_ID=' "$$file" | cut -d= -f2-)"; \
	      cur_tenant="$$(grep -E '^AZURE_TENANT_ID=' "$$file" | cut -d= -f2-)"; \
	      cur_client="$$(grep -E '^AZURE_CLIENT_ID=' "$$file" | cut -d= -f2-)"; \
	      cur_secret="$$(grep -E '^AZURE_CLIENT_SECRET=' "$$file" | cut -d= -f2-)"; \
	    fi; \
	    read -r -p "AZURE_SUBSCRIPTION_ID [$$cur_sub]: " input_sub; input_sub="$${input_sub:-$$cur_sub}"; \
	    read -r -p "AZURE_TENANT_ID [$$cur_tenant]: " input_tenant; input_tenant="$${input_tenant:-$$cur_tenant}"; \
	    read -r -p "AZURE_CLIENT_ID [$$cur_client]: " input_client; input_client="$${input_client:-$$cur_client}"; \
	    read -r -s -p "AZURE_CLIENT_SECRET [keep existing]: " input_secret; echo; input_secret="$${input_secret:-$$cur_secret}"; \
	    if [ -z "$$input_sub" ] || [ -z "$$input_tenant" ] || [ -z "$$input_client" ] || [ -z "$$input_secret" ]; then echo "subscription id, tenant id, client id and client secret are required" >&2; exit 1; fi; \
	    printf "AZURE_SUBSCRIPTION_ID=%s\nAZURE_TENANT_ID=%s\nAZURE_CLIENT_ID=%s\nAZURE_CLIENT_SECRET=%s\n" "$$input_sub" "$$input_tenant" "$$input_client" "$$input_secret" > "$$file"; \
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

i18n-check:
	$(PYTHON) i18n/manage.py --check $(ARGS)

i18n-update:
	$(PYTHON) i18n/manage.py --update $(ARGS)

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
