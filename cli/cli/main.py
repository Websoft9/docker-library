from __future__ import annotations

from rich.console import Console
from rich import box
from rich.table import Table
import typer

from cli import app as app_ops
from cli import validate, versions
from cli.output import print_output

HELP_OPTIONS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(name="libs", help="docker-library automation interface", context_settings=HELP_OPTIONS)


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
        "  libs scan --selection weekly --date 2026-08-17 --json\n"
        "  libs scan --selection all-active --max-pages 2"
    ),
)
def scan_command(
    selection: str = typer.Option("all-active", help="all-active | due | weekly | monthly | quarterly"),
    target_date: str | None = typer.Option(None, "--date", help="Date used for cadence selection in YYYY-MM-DD format"),
    plan_only: bool = typer.Option(False, help="Only list selected apps without remote version checks"),
    max_pages: int = typer.Option(1, help="Maximum number of Docker Hub pages"),
    page_size: int = typer.Option(100, help="Number of tags per Docker Hub page"),
    app_name: str | None = typer.Option(None, "--app", help="Scan only this app"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Scan upstream versions for selected apps."""
    payload = versions.scan_apps(
        selection=selection,
        target_date=target_date,
        plan_only=plan_only,
        max_pages=max_pages,
        page_size=page_size,
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


def run() -> None:
    app()
