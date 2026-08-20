from __future__ import annotations

import json

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from libs import app as app_ops
from libs import dblifecycle, drift, http, newapp, validate, versions
from libs.metadata import app_dir
from libs.output import print_output


HELP_OPTIONS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(name="libs", help="docker-library automation interface", context_settings=HELP_OPTIONS)


@app.callback()
def main_callback(
    proxy: str | None = typer.Option(None, "--proxy", help="Proxy URL for network calls, e.g. socks5h://127.0.0.1:1089"),
) -> None:
    http.normalize_proxy_env(proxy)


@app.command("proxy")
def proxy_command(
    set_url: str | None = typer.Option(None, "--set", help="Save a proxy URL to local config"),
    clear: bool = typer.Option(False, "--clear", help="Remove the saved proxy"),
) -> None:
    """Show, save, or clear the proxy used when the environment has none."""
    if set_url:
        http.save_proxy(set_url)
        typer.echo(f"saved proxy: {set_url}")
        return
    if clear:
        http.clear_proxy()
        typer.echo("saved proxy removed")
        return
    current = http.detect_proxy()
    typer.echo(current or "no proxy configured")


@app.command("list")
def list_command(
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived apps"),
    scope: str | None = typer.Option(None, "--scope", help="Filter by scope: public | internal"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """List active apps with maintenance metadata."""
    output = app_ops.collect_apps(include_archived=include_archived, scope=scope)
    if not as_json:
        active = app_ops.collect_apps(include_archived=False)
        all_apps = app_ops.collect_apps(include_archived=True)
        internal = sum(1 for item in active if item["scope"] == "internal")
        public = len(active) - internal
        archived = len(all_apps) - len(active)
        Console().print(
            f"[dim]total {len(all_apps)} | active {len(active)} (public {public}, internal {internal}) | archived {archived}[/dim]"
        )
        if not include_archived:
            Console().print("[dim]use --include-archived to show archived apps[/dim]")
        table = Table("name", "status", "cadence", "update policy", "scope", header_style="dim", box=box.SIMPLE)
        for item in output:
            table.add_row(item["name"], item["status"], item["cadence"], item["update_policy"], item["scope"])
        Console().print(table)
        return
    print_output(output, as_json)


@app.command("info")
def info_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Show one app's details and maintenance metadata."""
    try:
        payload = app_ops.collect_app_info(app_name)
    except FileNotFoundError:
        raise typer.Exit(code=4)
    print_output(payload, as_json)


@app.command(
    "scan",
    epilog=(
        "Examples:\n"
        "  libs scan --selection due --plan-only\n"
        "  libs scan --app wordpress\n"
        "  libs scan --app wordpress --major-ahead 5 --json"
    ),
)
def scan_command(
    selection: str = typer.Option("all-active", help="all-active | due | weekly | monthly | quarterly"),
    target_date: str | None = typer.Option(None, "--date", help="Date used for cadence selection in YYYY-MM-DD format"),
    plan_only: bool = typer.Option(False, help="Only list selected apps without remote version checks"),
    page_size: int = typer.Option(100, help="Number of tags per Docker Hub page"),
    major_ahead: int = typer.Option(3, help="How many future majors to probe"),
    app_name: str | None = typer.Option(None, "--app", help="Scan only this app"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Scan upstream versions for selected apps."""
    payload = versions.scan_apps(
        selection=selection,
        target_date=target_date,
        plan_only=plan_only,
        page_size=page_size,
        major_ahead=major_ahead,
        app_filter=app_name,
    )
    print_output(payload, as_json)


@app.command("check")
def check_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    gate: str = typer.Option("all", "--gate", help="all | structure | policy"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Run quality gate checks for one app."""
    payload = validate.check_app(app_name, gate=gate)
    print_output(payload, as_json)
    if not payload["ok"]:
        raise typer.Exit(code=1)


@app.command("report")
def report_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Generate a short readiness report for owner E2E."""
    check = validate.check_app(app_name, gate="all")
    payload = {
        "app": app_name,
        "decision": "ready-for-e2e" if check["ok"] else "blocked",
        "automated_checks": {
            "structure": check["structure"],
            "policy": check["policy"],
        },
        "owner_e2e_focus": [],
    }
    print_output(payload, as_json)
    if payload["decision"] != "ready-for-e2e":
        raise typer.Exit(code=1)


@app.command("archive")
def archive_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    reason: str = typer.Option("owner-retired", help="Archive reason"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview archive actions"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Archive one app out of active maintenance."""
    try:
        payload = app_ops.archive_app(app_name, reason=reason, dry_run=dry_run)
    except FileNotFoundError:
        raise typer.Exit(code=4)
    print_output(payload, as_json)


@app.command("restore")
def restore_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    cadence: str = typer.Option("monthly", help="Maintenance cadence after restore"),
    update_policy: str = typer.Option("patch-minor", help="Update policy after restore"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview restore actions"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Restore one archived app back to active maintenance."""
    try:
        payload = app_ops.restore_app(app_name, cadence=cadence, update_policy=update_policy, dry_run=dry_run)
    except FileNotFoundError:
        raise typer.Exit(code=4)
    except FileExistsError:
        raise typer.BadParameter(f"apps/{app_name} already exists; use app-update instead")
    print_output(payload, as_json)


@app.command("drift")
def drift_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """List dependency images and compare upstream compose drift."""
    target = app_dir(app_name)
    if not target:
        raise typer.Exit(code=4)

    compose_path = target / "docker-compose.yml"
    if not compose_path.exists():
        raise typer.Exit(code=4)

    compose = drift.parse_compose(compose_path)
    payload = {
        "app": app_name,
        "dependency_images": drift.dependency_images(compose),
        "compose_source": {
            "declared": False,
            "type": None,
            "url": None,
        },
        "config_source": {
            "declared": False,
            "type": None,
            "url": None,
        },
        "compose_drift": {
            "status": "not-declared",
            "diff": None,
            "error": None,
        },
        "config_drift": {
            "status": "not-declared",
            "diff": None,
            "error": None,
        },
    }

    variables_path = target / "variables.json"
    if variables_path.exists():
        variables = json.loads(variables_path.read_text(encoding="utf-8"))
        upstream = variables.get("upstream") or {}
        compose_group = upstream.get("compose") or {}
        compose_url = compose_group.get("compose")
        compose_source = {"type": "raw-compose", "url": compose_url} if compose_url else (upstream.get("compose_source") or {})
        config_url = compose_group.get("env")
        config_source = {"type": "raw-env", "url": config_url} if config_url else (upstream.get("config_source") or {})
        payload["compose_source"] = {
            "declared": bool(compose_source.get("type") and compose_source.get("url")),
            "type": compose_source.get("type"),
            "url": compose_source.get("url"),
        }
        payload["config_source"] = {
            "declared": bool(config_source.get("type") and config_source.get("url")),
            "type": config_source.get("type"),
            "url": config_source.get("url"),
        }
        if compose_source.get("type") == "raw-compose" and compose_source.get("url"):
            upstream_compose, error = drift.fetch_upstream_compose(compose_source["url"])
            if error:
                payload["compose_drift"] = {
                    "status": "source-error",
                    "diff": None,
                    "error": error,
                }
            else:
                payload["compose_drift"] = {
                    "status": "ok",
                    "diff": drift.diff_services(compose, upstream_compose),
                    "error": None,
                }

        if config_source.get("type") in ("raw-env", "raw-yaml") and config_source.get("url"):
            upstream_text, error = drift.fetch_upstream_text(config_source["url"])
            if error:
                payload["config_drift"] = {
                    "status": "source-error",
                    "diff": None,
                    "error": error,
                }
            else:
                local_env = drift.parse_env_file(target / ".env")
                upstream_env = drift.parse_env_text(upstream_text)
                payload["config_drift"] = {
                    "status": "ok",
                    "diff": drift.diff_config(local_env, upstream_env),
                    "error": None,
                }

    print_output(payload, as_json)


@app.command("db-refresh")
def db_refresh_command(
    engine: str | None = typer.Option(None, "--engine", help="Refresh only one engine"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Refresh the DB lifecycle snapshot from endoflife.date."""
    try:
        payload = dblifecycle.refresh_lifecycle(engine=engine)
    except ValueError as error:
        raise typer.BadParameter(str(error))
    except Exception as error:
        typer.echo(f"refresh failed: {error}", err=True)
        raise typer.Exit(code=1)
    print_output(payload, as_json)


@app.command("new-app")
def new_app_command(
    issue: str | None = typer.Option(None, "--from-issue", help="Issue block file, or - for stdin"),
    validate_only: str | None = typer.Option(None, "--validate-issue", help="Validate an issue block file, or - for stdin; no files written"),
    name: str | None = typer.Option(None, "--name", help="App name"),
    trademark: str | None = typer.Option(None, "--trademark", help="Brand display name"),
    version: str | None = typer.Option(None, "--version", help="Image version, e.g. 7.0"),
    repo: str | None = typer.Option(None, "--repo", help="Image reference, e.g. wordpress or ghcr.io/ns/img"),
    docs_github: str | None = typer.Option(None, "--docs-github", help="Project repository URL"),
    docs_image: str | None = typer.Option(None, "--docs-image", help="Official image registry URL"),
    docs_install: str | None = typer.Option(None, "--docs-install", help="Official install reference URL"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview files without writing"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Validate a new app request and scaffold the app package skeleton."""
    docs = {}
    for key, value in (("github", docs_github), ("image", docs_image), ("install", docs_install)):
        if value:
            docs[key] = value

    if validate_only:
        block = newapp.parse_issue_block(newapp.read_issue_source(validate_only))
        if block is None:
            typer.echo("no new-app-request yaml block found", err=True)
            raise typer.Exit(code=2)
        errors = newapp.validate_request(block)
        print_output({"valid": not errors, "errors": errors}, as_json)
        if errors:
            raise typer.Exit(code=1)
        return

    if issue:
        block = newapp.parse_issue_block(newapp.read_issue_source(issue))
        if block is None:
            typer.echo("no new-app-request yaml block found", err=True)
            raise typer.Exit(code=2)
        errors = newapp.validate_request(block)
        if errors:
            print_output({"valid": False, "errors": errors}, as_json)
            raise typer.Exit(code=1)
        name = block.get("name")
        trademark = block.get("trademark")
        docs = block.get("docs") or {}

    if not name or not trademark or not version or not repo:
        raise typer.BadParameter("--name, --trademark, --version, and --repo are required (or use --from-issue plus --version/--repo)")

    try:
        payload = newapp.scaffold(
            name=name,
            trademark=trademark,
            version=version,
            repo=repo,
            docs=docs,
            dry_run=dry_run,
        )
    except ValueError as error:
        raise typer.BadParameter(str(error))
    except FileExistsError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    print_output(payload, as_json)


def run() -> int | None:
    try:
        app()
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        return 4
