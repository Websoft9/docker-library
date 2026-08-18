from __future__ import annotations

import json
from datetime import date, datetime

import typer

from cli.metadata import active_app_dirs, resolve_app_metadata
from cli.output import print_output
from cli.versioning import (
    convert_to_dockerhub_api_url,
    find_latest_version,
    get_current_versions,
    get_dockerhub_tags,
)

app = typer.Typer(help="Scan upstream versions", context_settings={"help_option_names": ["-h", "--help"]})


def _parse_target_date(raw_date: str | None) -> date:
    if not raw_date:
        return date.today()
    return datetime.strptime(raw_date, "%Y-%m-%d").date()


def _cadence_matches(cadence: str, target_date: date) -> bool:
    if cadence == "weekly":
        return target_date.weekday() == 0
    if cadence == "monthly":
        return target_date.day == 1
    if cadence == "quarterly":
        return target_date.day == 1 and target_date.month in (1, 4, 7, 10)
    return False


def _selected(app_name: str, selection: str, target_date: date) -> tuple[bool, str]:
    metadata = resolve_app_metadata(app_name)
    if metadata.status == "archived":
        return False, "archived"
    if selection == "all-active":
        return True, "all-active"
    if selection == "due":
        return _cadence_matches(metadata.cadence, target_date), metadata.cadence
    return metadata.cadence == selection, metadata.cadence


def scan_apps(
    selection: str = "all-active",
    target_date: str | None = None,
    plan_only: bool = False,
    max_pages: int = 1,
    page_size: int = 100,
    app_filter: str | None = None,
) -> list[dict]:
    target = _parse_target_date(target_date)
    output = []

    for app_dir in active_app_dirs():
        if app_filter and app_dir.name != app_filter:
            continue
        included, selected_by = _selected(app_dir.name, selection, target)
        if not included:
            continue

        variables_path = app_dir / "variables.json"
        if not variables_path.exists():
            continue

        metadata = resolve_app_metadata(app_dir.name)
        variables = json.loads(variables_path.read_text(encoding="utf-8"))
        current_versions, all_versions = get_current_versions(variables.get("edition", []))
        current_version_strs = [str(current) for current in current_versions]
        payload = {
            "name": variables["name"],
            "status": metadata.status,
            "cadence": metadata.cadence,
            "update_policy": metadata.update_policy,
            "selected_by": selected_by,
            "target_date": target.isoformat(),
            "current_version": all_versions if plan_only else current_version_strs,
            "version_from": variables.get("version_from", ""),
        }

        if plan_only:
            output.append(payload)
            continue

        if not variables.get("release", False):
            payload["error"] = "App release=false"
            payload["latest_version"] = None
            output.append(payload)
            continue

        if not current_versions or ("latest" in current_version_strs and len(current_version_strs) == 1):
            payload["error"] = "No valid current versions found"
            payload["latest_version"] = None
            output.append(payload)
            continue

        highest_version = max(current for current in current_versions if current != "latest")
        api_url = convert_to_dockerhub_api_url(variables.get("version_from", ""))
        if not api_url:
            payload["error"] = "Invalid version_from URL or not a Docker Hub URL"
            payload["latest_version"] = None
            output.append(payload)
            continue

        try:
            tags = get_dockerhub_tags(api_url, max_pages=max_pages, page_size=page_size)
            payload["latest_version"] = find_latest_version(tags, str(highest_version))
        except Exception as error:
            payload["error"] = f"Failed to fetch tags: {error}"
            payload["latest_version"] = None

        output.append(payload)

    return output


@app.command()
def scan(
    selection: str = typer.Option("all-active", help="all-active | due | weekly | monthly | quarterly"),
    target_date: str | None = typer.Option(None, "--date", help="Date used for cadence selection in YYYY-MM-DD format"),
    plan_only: bool = typer.Option(False, help="Only list selected apps without remote version checks"),
    max_pages: int = typer.Option(1, help="Maximum number of Docker Hub pages"),
    page_size: int = typer.Option(100, help="Number of tags per Docker Hub page"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    output = scan_apps(selection=selection, target_date=target_date, plan_only=plan_only, max_pages=max_pages, page_size=page_size)
    print_output(output, as_json)
