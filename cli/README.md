# CLI

`libs` is the docker-library automation interface. Run it from the repository root or any subdirectory inside the repository.

## Install

```bash
make install
```

Contentful commands require the `contentful_management` Python SDK, which `make install` installs as a base dependency.

Windows PowerShell:

```powershell
.\make.ps1 install
```

## Usage

```bash
make cli     # enter an activated shell
libs scan --selection due --json
libs app-check --app wordpress --json
```

Windows PowerShell:

```powershell
.\make.ps1 libs scan --selection due --json
.\make.ps1 libs app-check --app wordpress --json
```

Or without activating:

```bash
make libs ARGS="check --app wordpress --json"
```

One-off without install:

```bash
python3 -m venv .venv
.venv/bin/pip install -e cli/
.venv/bin/python -m libs scan --selection due --json
```

Windows one-off:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e cli/
.\.venv\Scripts\python.exe -m libs scan --selection due --json
```

## Commands

- `libs list` - list active apps
- `libs app-info --app <name>` - show one app
- `libs scan` - scan upstream versions
- `libs app-check --app <name>` - run structure + policy gates
- `libs app-check --app <name> --gate structure`
- `libs app-check --app <name> --gate policy`
- `libs app-report --app <name>` - generate a short readiness report
- `libs app-archive --app <name> --dry-run` - preview archive actions
- `libs app-restore --app <name> --dry-run` - preview restore actions
- `libs app-drift --app <name>` - list dependency images and compare upstream compose drift
- `libs db-refresh` - refresh the DB lifecycle snapshot from endoflife.date
- `libs maintenance-check` - validate maintenance/archive metadata against the app tree
- `libs app-new --name <name> --trademark <brand> --dry-run` - preview a new app scaffold
- `libs app-new --name <name> --trademark <brand> --upstream-releases <url> --upstream-compose <url> --upstream-env <url>` - prefill optional upstream sources used by scan, drift, and README generation
- `libs app-gen-readme --app <name>` - regenerate one app's README from variables.json
- `libs catalog-push --app <name>` - preview pushing repo catalog + machine fields to Contentful (use `--apply` to write)
- `libs catalog-update --app <name> --fields '<json>'` - preview updating fields on an existing Contentful product entry (use `--apply` to write); e.g. `--fields '{"appStore": false, "production": false}'`
  - Direct `libs` invocation: single-quote the JSON and use real double quotes inside, e.g. `--fields '{"appStore": false}'`
  - `make libs ARGS="..."` wrapper: the outer double quotes need escapes, e.g. `make libs ARGS="catalog-update --app <name> --fields '{\"appStore\": false}'"`
- `libs app-deploy --app <name> [--ssh-host <ip>] [--progress] [--verbose]` - deploy one app locally or remotely; `--progress` prints step headers to stderr and `--verbose` also prints raw command output
- `libs app-deploy --app <name> --version <tag>` - deploy a specific image tag by overriding `W9_VERSION` without modifying the repo `.env`
- `libs app-down --app <name> [--ssh-host <ip>] [--progress] [--json]` - tear one app down with `docker compose down -v`
- `libs appstore-sync --app <name> --ssh-host <ip> [--progress] [--verbose]` - patch remote `product_en.json` / `product_zh.json` distribution and sync one app directory for appstore testing
- `libs appstore-deploy --app <name> --ssh-host <ip> [--progress] [--verbose]` - deploy one app into a websoft9 container appstore (not implemented yet; pending the websoft9 container CLI)
- remote-aware commands suppress the routine `known hosts` add warning from ephemeral SSH targets; real stderr still passes through
- `libs proxy` - show, save, or clear the saved proxy
- `libs help` - show help, same as `libs --help`

Options: `--json`, `--progress`, `--verbose`, `--plan-only`, `--selection`, `--date`, `--include-archived`, `--scope`, `--major-ahead`, `--proxy`, `-h` / `--help`.

Shared execution options:
- `--json` keeps the final payload on `stdout`
- `--progress` writes step-level progress to `stderr`
- `--verbose` writes step-level progress and raw subprocess output to `stderr`
- only long-running or execution-style commands expose `--progress` and `--verbose`

Network behavior:
- default request timeout is 15s, override with `LIBS_HTTP_TIMEOUT`
- resolution order: `--proxy` > environment variables > `cli/proxy.conf`
- a wildcard `no_proxy=*` is ignored when a proxy is present
- `make cli` and `make install` snapshot the host proxy into `cli/proxy.conf`
- `make.ps1 install` snapshots the host proxy into `cli/proxy.conf`
- manage the saved proxy with `libs proxy`, `libs proxy --set <url>`, `libs proxy --clear`
- `cli/proxy.conf` is machine-local and gitignored

Credentials:
- provider-specific token files live under `.secrets/`, for example `.secrets/contentful.env` and `.secrets/cloudflare.env` (gitignored)
- each provider file stores the token directly as a standard env var, e.g. `CONTENTFUL_ACCESS_TOKEN=...` or `CLOUDFLARE_API_TOKEN=...`
- a command may accept a per-invocation token flag (e.g. `--token`) and an explicit provider env file path (e.g. `--env-file`) as overrides
- resolution order: command flag > explicit `--env-file` > environment variable > default provider file
- CI keeps passing secrets as environment variables from GitHub Actions secrets; it does not use `.secrets/`

Run from the repository root or a subdirectory inside it. The CLI now refuses to run outside the repository so it cannot read or write the wrong `apps/` or `metadata/` tree by accident. CLI does not depend on `build/`.
