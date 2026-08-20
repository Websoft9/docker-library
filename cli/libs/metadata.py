from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from libs.repo import repo_path


@dataclass
class AppMetadata:
    status: str
    cadence: str
    update_policy: str
    archive_reason: str | None = None
    contentful: dict | None = None


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_maintenance() -> dict:
    return _load_yaml(repo_path("metadata", "maintenance.yaml"))


def load_archive() -> dict:
    return _load_yaml(repo_path("metadata", "archive.yaml"))


def resolve_archive_entries(data: dict) -> dict[str, dict]:
    defaults = data.get("defaults") or {}
    apps = data.get("apps") or []
    overrides = data.get("overrides") or {}
    resolved: dict[str, dict] = {}

    for app in apps:
        resolved[app] = dict(defaults)
        resolved[app].update(overrides.get(app) or {})

    for app, extra in overrides.items():
        if app not in resolved:
            resolved[app] = dict(defaults)
            resolved[app].update(extra or {})

    return resolved


def resolve_app_metadata(app_name: str) -> AppMetadata:
    maintenance = load_maintenance()
    archive = resolve_archive_entries(load_archive())
    defaults = maintenance.get("defaults") or {}

    status = defaults.get("status", "active")
    cadence = defaults.get("cadence", "monthly")
    update_policy = defaults.get("update_policy", "patch-minor")
    archive_reason = None
    contentful = None

    for bucket, apps in (maintenance.get("cadence") or {}).items():
        if app_name in (apps or []):
            cadence = bucket
            break

    for bucket, apps in (maintenance.get("update_policy") or {}).items():
        if app_name in (apps or []):
            update_policy = bucket
            break

    lifecycle = maintenance.get("lifecycle") or {}
    if app_name in (lifecycle.get("frozen") or []):
        status = "frozen"

    if app_name in archive:
        status = "archived"
        cadence = "none"
        update_policy = "none"
        archive_reason = archive[app_name].get("archive_reason")
        contentful = archive[app_name].get("contentful")

    return AppMetadata(
        status=status,
        cadence=cadence,
        update_policy=update_policy,
        archive_reason=archive_reason,
        contentful=contentful,
    )


def app_dir(app_name: str) -> Path | None:
    active = repo_path("apps", app_name)
    if active.exists():
        return active

    archived = repo_path("archive", "apps", app_name)
    if archived.exists():
        return archived

    return None


def active_app_dirs() -> list[Path]:
    apps_root = repo_path("apps")
    if not apps_root.exists():
        return []
    return sorted(path for path in apps_root.iterdir() if path.is_dir())
