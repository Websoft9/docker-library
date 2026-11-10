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
make libs ARGS="app-check --app wordpress --json"
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
- `libs image-stats` - summarize image usage across all apps by registry: docker.io total with the Docker official vs docker.io third-party split (official % of docker.io), plus other registries; `--app <name>` for one app, `--include-archived` adds archived apps
- `libs app-info --app <name>` - show one app; `database_connections` contains declarations, `database_metadata` contains validation, `database_lifecycle` contains lifecycle findings (`database` remains the lifecycle compatibility alias), `secrets` contains declared `env.secrets` entries, and `secret_metadata` contains secret template validation; no credential source values are resolved
- Complex app packages declare known bundled database information only and do not offer external databases. Missing fields or unknown managed stores do not block other known declarations; metadata does not require runtime rewiring or initialization separation. See [the database connection specification](../docs/app-database-connection-spec.md#13-复杂应用信息优先与本轮收缩).
- `libs scan` - scan upstream versions
- `libs app-check --app <name>` - run structure + policy + database declaration + secret template gates; legacy database objects are accepted with migration warnings during transition
- `libs app-check --app <name> --gate database-metadata` - validate declaration shape, component IDs, Compose service references and dictionary drivers; does not connect to databases
- `libs app-check --app <name> --gate secrets` - validate `env.secrets` declarations against `metadata/secret-rules.json` (plain shape templates, comma-separated lists, `base64`/`fernet`/`jwt:<SECRET_KEY>` rules, and variable references). The dictionary's typed `generator`, `encoding`, `bytes`, and `algorithm` options drive special-template validation; missing or invalid dictionaries fail the gate. This does not generate keys, establish consumer compatibility, prove application-specific key lengths, or rotate credentials; see [the secret contract](../docs/app-secret-spec.md).
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
- `libs appstore-sync --app <name> --ssh-host <ip> [--version <tag>] [--progress] [--verbose]` - validate declarations before remote writes, then sync shared `metadata/database-types.json` and `metadata/secret-rules.json` with checksum verification and backup, followed by the app directory and optional `metadata/catalog/<app>.json`; finally run `websoft9 appstore reload --json` inside the container. A reload failure fails the command; success includes `catalog_refreshed: true` and rollback commands for the app and both dictionaries (including removal when a dictionary did not previously exist). These returned commands are manual recovery steps, not an automatic multi-file transaction. `--version` overrides `W9_VERSION` in the synced copy only. Confirm the consumer supports the reload CLI, database declarations, secret object declarations, and their generators as applicable; publishing metadata alone does not add consumer capabilities. No library schema 2 upgrade is required.
- `libs appstore-deploy --app <name> --ssh-host <ip> [--progress] [--verbose]` - deploy one app into a websoft9 container appstore (not implemented yet; pending the websoft9 container CLI)
- remote-aware commands suppress the routine `known hosts` add warning from ephemeral SSH targets; real stderr still passes through
- `libs proxy` - show, save, or clear the saved proxy
- `libs help` - show help, same as `libs --help`

## Make Ops

These server-side operations are exposed as `make` targets, not `libs` commands. They accept the same options through `ARGS`.

- `make dns-bind ARGS="[--domain <domain>] [--target local|remote] [--ip <ip>] [--json]"` - point the wildcard record `*.<domain>` at the remote host or `127.0.0.1`; it creates the record when missing, updates it when the value differs, and is a no-op (`action = unchanged`) when the IP already matches, so repeated runs never error; `--domain` defaults to `DNS_DOMAIN`, and `--target` defaults to `TARGET` in `.secrets/remote.env` (add `--ssh-host` to override)
  - on success it also runs `websoft9 setconfig --section domain --key wildcard_domain --value <domain>` inside the Websoft9 container to bind the platform domain; the container name comes from `CONTAINER` in `.secrets/remote.env` (default `websoft9`, override with `--container`); if the container is absent or unreachable this step is skipped silently and reported as `container_config.status = skipped`; pass `--no-container` to skip it explicitly
- `make dns-delete ARGS="[--domain <domain>] [--json]"` - delete the single wildcard record `*.<domain>` managed for the domain; errors when it is missing or ambiguous
- `make websoft9-upgrade ARGS="[--container <name>] [--tag <tag>] [--tag-var <var>] [--compose-dir <dir>] [--target local|remote] [--ssh-host <ip>] [--progress] [--verbose]"` - upgrade the Websoft9 platform container: set the image tag (default `dev`), run `docker compose pull`, then `docker compose up -d`; the compose project is discovered from the container labels unless `--compose-dir` is given

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
- provider-specific token files live under `.secrets/`, for example `.secrets/contentful.env`, `.secrets/cloudflare.env`, and `.secrets/dns.env` (gitignored)
- `make connector` also writes cloud-provider credential files (`.secrets/aliyun.env`, `.secrets/aws.env`, `.secrets/azure.env`) for `alibabacloud`, `aws`, and `azure`
- each provider file stores the token directly as a standard env var, e.g. `CONTENTFUL_ACCESS_TOKEN=...`, `CLOUDFLARE_API_TOKEN=...`, or `DNS_PROVIDER=aliyun` / `DNS_KEY_ID=...` / `DNS_KEY_SECRET=...` (with an optional `DNS_DOMAIN=libs.websoft9.cn`); `DNS_PROVIDER` defaults to `aliyun`, the only DNS provider implemented today
- a command may accept a per-invocation token flag (e.g. `--token`) and an explicit provider env file path (e.g. `--env-file`) as overrides
- resolution order: command flag > explicit `--env-file` > environment variable > default provider file
- CI keeps passing secrets as environment variables from GitHub Actions secrets; it does not use `.secrets/`

Run from the repository root or a subdirectory inside it. The CLI now refuses to run outside the repository so it cannot read or write the wrong `apps/` or `metadata/` tree by accident. CLI does not depend on the publishing scripts under `ci/scripts/`.
