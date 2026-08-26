# CLI

`libs` is the docker-library automation interface. Run it from the repository root or any subdirectory inside the repository.

## Install

```bash
make install
```

Windows PowerShell:

```powershell
.\make.ps1 install
```

## Usage

```bash
make cli     # enter an activated shell
libs scan --selection due --json
libs check --app wordpress --json
```

Windows PowerShell:

```powershell
.\make.ps1 libs scan --selection due --json
.\make.ps1 libs check --app wordpress --json
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
- `libs info --app <name>` - show one app
- `libs scan` - scan upstream versions
- `libs check --app <name>` - run structure + policy gates
- `libs check --app <name> --gate structure`
- `libs check --app <name> --gate policy`
- `libs report --app <name>` - generate a short readiness report
- `libs archive --app <name> --dry-run` - preview archive actions
- `libs restore --app <name> --dry-run` - preview restore actions
- `libs drift --app <name>` - list dependency images and compare upstream compose drift
- `libs db-refresh` - refresh the DB lifecycle snapshot from endoflife.date
- `libs check-maintenance` - validate maintenance/archive metadata against the app tree
- `libs new-app --name <name> --trademark <brand> --dry-run` - preview a new app scaffold
- `libs gen-readme --app <name>` - regenerate one app's README from variables.json
- `libs contentful-create --app <name>` - preview a Contentful product entry (use `--apply` to write)
- `libs app-deploy --app <name> [--ssh-host <ip>] [--progress] [--verbose]` - deploy one app locally or remotely; `--progress` prints step headers to stderr and `--verbose` also prints raw command output
- `libs app-deploy --app <name> --version <tag>` - deploy a specific image tag by overriding `W9_VERSION` without modifying the repo `.env`
- `libs app-down --app <name> [--ssh-host <ip>] [--progress] [--json]` - tear one app down with `docker compose down -v`
- `libs appstore-sync --app <name> --ssh-host <ip> [--progress] [--verbose]` - patch remote `product_en.json` / `product_zh.json` distribution and sync one app directory for appstore testing
- `libs appstore-deploy --app <name> --ssh-host <ip> [--progress] [--verbose]` - deploy one app into a websoft9 container appstore (not implemented yet; pending the websoft9 container CLI)
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

Run from the repository root or a subdirectory inside it. The CLI now refuses to run outside the repository so it cannot read or write the wrong `apps/` or `metadata/` tree by accident. CLI does not depend on `build/`.
