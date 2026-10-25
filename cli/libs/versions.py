from __future__ import annotations

import json
import time
from datetime import date, datetime

import typer

from libs import http, scan_state
from libs.metadata import active_app_dirs, resolve_app_metadata
from libs.output import print_output
from libs.sources import detect_source_type, fetch_candidates, fetch_verified_candidates
from libs.versioning import get_current_versions, update_status


app = typer.Typer(help="Scan upstream versions", context_settings={"help_option_names": ["-h", "--help"]})


def _parse_target_date(raw_date: str | None) -> date:
    if not raw_date:
        return date.today()
    return datetime.strptime(raw_date, "%Y-%m-%d").date()


def _selected(app_name: str, selection: str, target_date: date, entry: dict | None) -> tuple[bool, str]:
    metadata = resolve_app_metadata(app_name)
    if metadata.status == "archived":
        return False, "archived"
    if selection == "all-active":
        return True, "all-active"
    if selection == "due":
        if entry is None:
            raise ValueError("state is required when selection is due")
        return scan_state.app_due(entry, metadata.cadence, app_name, target_date)
    return metadata.cadence == selection, metadata.cadence


def resolve_source_type(variables: dict) -> str:
    upstream = variables.get("upstream") or {}
    image = upstream.get("image")
    if image:
        return detect_source_type(image) or "unknown"
    return "unknown"


def scan_apps(
    selection: str = "all-active",
    target_date: str | None = None,
    plan_only: bool = False,
    page_size: int = 100,
    major_ahead: int = 3,
    app_filter: str | None = None,
    network_timeout: float = 15.0,
    state: dict | None = None,
    limit: int | None = None,
) -> list[dict]:
    started = time.monotonic()
    http.reset_network_state(network_timeout)
    target = _parse_target_date(target_date)
    if selection == "due" and state is None:
        raise ValueError("state is required when selection is due")

    state_apps = (state or {}).get("apps")
    if state_apps is None:
        state_apps = {}
    if not isinstance(state_apps, dict):
        raise scan_state.ScanStateError("state.apps must be an object")
    candidates = []

    for app_dir in active_app_dirs():
        if app_filter and app_dir.name != app_filter:
            continue

        variables_path = app_dir / "variables.json"
        if not variables_path.exists():
            continue

        metadata = resolve_app_metadata(app_dir.name)
        entry = state_apps.get(app_dir.name)
        if entry is None:
            entry = {}
        if not isinstance(entry, dict):
            raise scan_state.ScanStateError(f"state entry for {app_dir.name} must be an object")
        included, selected_by = _selected(
            app_dir.name,
            selection,
            target,
            entry if state is not None else None,
        )
        if not included:
            continue

        variables = json.loads(variables_path.read_text(encoding="utf-8"))
        if selection == "due" and not variables.get("release", False):
            continue

        candidates.append({
            "app_dir": app_dir,
            "metadata": metadata,
            "selected_by": selected_by,
            "variables": variables,
            "attempt_at": entry.get("attempt_at") or "",
        })

    if selection == "due":
        candidates.sort(key=lambda item: (item["attempt_at"], item["app_dir"].name))
    if limit and limit > 0:
        candidates = candidates[:limit]

    output = []

    for candidate in candidates:
        app_dir = candidate["app_dir"]
        metadata = candidate["metadata"]
        selected_by = candidate["selected_by"]
        variables = candidate["variables"]
        current_versions, all_versions = get_current_versions(variables.get("edition", []))
        current_version_strs = [str(current) for current in current_versions]
        upstream = variables.get("upstream") or {}
        image_url = upstream.get("image") or ""
        payload = {
            "name": variables["name"],
            "status": metadata.status,
            "cadence": metadata.cadence,
            "update_policy": metadata.update_policy,
            "selected_by": selected_by,
            "target_date": target.isoformat(),
            "current_version": all_versions if plan_only else current_version_strs,
            "upstream_image": image_url,
            "source_type": resolve_source_type(variables),
            "release": variables.get("release"),
        }

        if plan_only:
            output.append(payload)
            continue

        if not variables.get("release", False) and not app_filter:
            payload["error"] = "App release=false"
            payload["latest_version"] = None
            payload["network"] = http.network_snapshot()
            payload["scan_elapsed_ms"] = int((time.monotonic() - started) * 1000)
            output.append(payload)
            continue

        if not current_versions or ("latest" in current_version_strs and len(current_version_strs) == 1):
            payload["error"] = "No valid current versions found"
            payload["latest_version"] = None
            payload["network"] = http.network_snapshot()
            payload["scan_elapsed_ms"] = int((time.monotonic() - started) * 1000)
            output.append(payload)
            continue

        highest_version = max(current for current in current_versions if current != "latest")
        releases = upstream.get("releases")
        if releases:
            latest_version, error = fetch_verified_candidates(
                payload["source_type"],
                image_url,
                detect_source_type(releases) or "github-tags",
                releases,
                str(highest_version),
                major_ahead=major_ahead,
                page_size=page_size,
            )
        else:
            latest_version, error = fetch_candidates(
                payload["source_type"],
                image_url,
                str(highest_version),
                major_ahead=major_ahead,
                page_size=page_size,
            )
        if error:
            payload["error"] = f"Failed to fetch tags: {error}"
            payload["latest_version"] = None
            payload["version_status"] = "unavailable"
        else:
            payload["latest_version"] = latest_version
            payload["version_status"] = update_status(str(highest_version), latest_version)

        payload["network"] = http.network_snapshot()
        payload["scan_elapsed_ms"] = int((time.monotonic() - started) * 1000)
        output.append(payload)

    return output


@app.command()
def scan(
    selection: str = typer.Option("all-active", help="all-active | due | weekly | monthly | quarterly"),
    target_date: str | None = typer.Option(None, "--date", help="Date used for cadence selection in YYYY-MM-DD format"),
    plan_only: bool = typer.Option(False, help="Only list selected apps without remote version checks"),
    max_pages: int = typer.Option(1, help="Deprecated; ignored"),
    page_size: int = typer.Option(100, help="Number of tags per Docker Hub page"),
    network_timeout: float = typer.Option(15.0, "--network-timeout", min=1.0, max=120.0, help="Total seconds for upstream network checks"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    _ = max_pages
    output = scan_apps(selection=selection, target_date=target_date, plan_only=plan_only, page_size=page_size, network_timeout=network_timeout)
    print_output(output, as_json)
