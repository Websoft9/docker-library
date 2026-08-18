# CLI

`libs` is the docker-library automation interface. Run it from the repository root.

## Install

```bash
make install
```

## Usage

```bash
make cli     # enter an activated shell
libs scan --selection due --json
libs check --app wordpress --json
```

Or without activating:

```bash
make libs ARGS="check --app wordpress --json"
```

One-off without install:

```bash
python3 -m venv .venv
.venv/bin/pip install -e cli/
.venv/bin/python -m cli scan --selection due --json
```

## Commands

- `libs list` - list active apps
- `libs info --app <name>` - show one app
- `libs scan` - scan upstream versions
- `libs check --app <name>` - run structure + policy
- `libs check --app <name> --gate structure`
- `libs check --app <name> --gate policy`
- `libs report --app <name>` - generate a short readiness report
- `libs archive --app <name> --dry-run` - preview archive actions

Options: `--json`, `--plan-only`, `--selection`, `--date`, `--include-archived`, `--scope`, `-h` / `--help`.

Run from the repository root. CLI does not depend on `build/`.
