from __future__ import annotations

import fcntl
import json
import shutil
from contextlib import contextmanager
from pathlib import Path

import typer
import yaml
from rich import box
from rich.console import Console
from rich.table import Table

from libs.metadata import active_app_dirs, app_dir, resolve_app_metadata
from libs.output import print_output
from libs.repo import relative_repo_path, repo_path


app = typer.Typer(help="Manage apps", context_settings={"help_option_names": ["-h", "--help"]})


def _app_names(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir())


def _has_root_dockerfile(target: Path | None) -> bool:
    return bool(target and (target / "Dockerfile").exists())


def collect_apps(include_archived: bool = False, scope: str | None = None) -> list[dict]:
    names = [path.name for path in active_app_dirs()]
    output = []

    for name in names:
        target = app_dir(name)
        metadata = resolve_app_metadata(name)
        item = {
            "name": name,
            "status": metadata.status,
            "cadence": metadata.cadence,
            "update_policy": metadata.update_policy,
            "scope": _app_scope(name),
            "dockerfile": _has_root_dockerfile(target),
        }
        if scope and item["scope"] != scope:
            continue
        output.append(item)

    if include_archived:
        for name in _app_names(repo_path("archive", "apps")):
            target = app_dir(name)
            metadata = resolve_app_metadata(name)
            item = {
                "name": name,
                "status": metadata.status,
                "cadence": metadata.cadence,
                "update_policy": metadata.update_policy,
                "scope": _app_scope(name),
                "dockerfile": _has_root_dockerfile(target),
            }
            if scope and item["scope"] != scope:
                continue
            output.append(item)

    output.sort(key=lambda item: item["name"])
    return output


def _app_scope(app_name: str) -> str:
    target = app_dir(app_name)
    if not target:
        return "public"
    variables_path = target / "variables.json"
    if not variables_path.exists():
        return "public"
    variables = json.loads(variables_path.read_text(encoding="utf-8"))
    return variables.get("scope", "public")


def _env_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _compose_summary(path: Path) -> dict:
    if not path.exists():
        return {"services": [], "images": [], "ports": []}
    compose = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    services = compose.get("services") or {}
    images = []
    ports = []
    for service_name, service in services.items():
        if not isinstance(service, dict):
            continue
        image = service.get("image")
        if isinstance(image, str):
            images.append({"service": str(service_name), "image": image})
        for entry in service.get("ports", []) or []:
            if isinstance(entry, dict):
                ports.append({
                    "service": str(service_name),
                    "published": entry.get("published"),
                    "target": entry.get("target"),
                })
            elif isinstance(entry, str):
                ports.append({"service": str(service_name), "published": entry, "target": None})
    return {"services": sorted(str(name) for name in services), "images": images, "ports": ports}


def _test_summary(path: Path) -> dict:
    if not path.exists():
        return {"declared": False, "cases": []}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cases = []
    for group in ("skip", "optional", "custom"):
        for case in payload.get(group) or []:
            if isinstance(case, dict):
                cases.append({
                    "group": group,
                    "id": case.get("id"),
                    "type": case.get("type"),
                })
    return {"declared": True, "cases": cases}


def collect_app_info(app_name: str) -> dict:
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)

    variables_path = target / "variables.json"
    variables = json.loads(variables_path.read_text(encoding="utf-8")) if variables_path.exists() else {}
    metadata = resolve_app_metadata(app_name)
    env_values = _env_values(target / ".env")
    compose_summary = _compose_summary(target / "docker-compose.yml")

    from libs.app_deploy import _compose_published_ports
    from libs.validate import _database_result

    return {
        "name": app_name,
        "path": relative_repo_path(target),
        "status": metadata.status,
        "cadence": metadata.cadence,
        "update_policy": metadata.update_policy,
        "archive_reason": metadata.archive_reason,
        "trademark": variables.get("trademark"),
        "release": variables.get("release"),
        "upstream_image": (variables.get("upstream") or {}).get("image"),
        "upstream": variables.get("upstream"),
        "requirements": variables.get("requirements"),
        "external_db": variables.get("externalDB"),
        "version": {
            "w9_version": env_values.get("W9_VERSION"),
            "declared": [
                str(value)
                for edition in variables.get("edition", [])
                if edition.get("dist") == "community"
                for value in edition.get("version", [])
            ],
        },
        "ports": compose_summary["ports"],
        "published_ports": _compose_published_ports(target, env_values),
        "services": compose_summary["services"],
        "images": compose_summary["images"],
        "credentials": variables.get("credentials"),
        "database": _database_result(target),
        "tests": _test_summary(target / "tests" / "cases.yml"),
        "env_keys": sorted(env_values),
    }


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _write_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)


@contextmanager
def _metadata_lock():
    lock_path = repo_path("metadata", ".app-metadata.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def archive_app(app_name: str, reason: str = "owner-retired", dry_run: bool = False) -> dict:
    with _metadata_lock():
        source = app_dir(app_name)
        if not source:
            raise FileNotFoundError(app_name)

        archive_target = repo_path("archive", "apps", app_name)
        already_archived = source == archive_target
        actions = {
            "app": app_name,
            "source": relative_repo_path(source),
            "target": relative_repo_path(archive_target),
            "reason": reason,
            "already_archived": already_archived,
            "dry_run": dry_run,
        }
        if already_archived:
            return actions

        maintenance_path = repo_path("metadata", "maintenance.yaml")
        archive_path = repo_path("metadata", "archive.yaml")
        maintenance = _read_yaml(maintenance_path)
        archive = _read_yaml(archive_path)

        for apps in (maintenance.get("cadence") or {}).values():
            if app_name in (apps or []):
                apps.remove(app_name)
        for apps in (maintenance.get("update_policy") or {}).values():
            if app_name in (apps or []):
                apps.remove(app_name)
        frozen = (maintenance.get("lifecycle") or {}).get("frozen") or []
        if app_name in frozen:
            frozen.remove(app_name)

        defaults = archive.setdefault("defaults", {
            "archive_reason": "owner-retired",
            "contentful": {"action": "archive", "production": False},
        })
        archive_apps = archive.setdefault("apps", [])
        if app_name not in archive_apps:
            archive_apps.append(app_name)
            archive_apps.sort()
        overrides = archive.setdefault("overrides", {})
        if reason != defaults.get("archive_reason"):
            overrides[app_name] = {"archive_reason": reason}

        if dry_run:
            actions["metadata_updated"] = True
            return actions

        archive_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(archive_target))
        _write_yaml(maintenance_path, maintenance)
        _write_yaml(archive_path, archive)
        actions["metadata_updated"] = True
        return actions


def restore_app(app_name: str, cadence: str = "monthly", update_policy: str = "patch-minor", dry_run: bool = False) -> dict:
    with _metadata_lock():
        source = repo_path("archive", "apps", app_name)
        if not source.exists():
            raise FileNotFoundError(app_name)
        target = repo_path("apps", app_name)
        if target.exists():
            raise FileExistsError(app_name)

        maintenance_path = repo_path("metadata", "maintenance.yaml")
        archive_path = repo_path("metadata", "archive.yaml")
        maintenance = _read_yaml(maintenance_path)
        archive = _read_yaml(archive_path)

        actions = {
            "app": app_name,
            "source": relative_repo_path(source),
            "target": relative_repo_path(target),
            "cadence": cadence,
            "update_policy": update_policy,
            "dry_run": dry_run,
        }

        archived_apps = archive.get("apps") or []
        overrides = archive.get("overrides") or {}
        registered = app_name in archived_apps or app_name in overrides
        if not registered:
            actions["warning"] = f"{app_name} is not registered in metadata/archive.yaml; directory move only"
        else:
            archive["apps"] = sorted(a for a in archived_apps if a != app_name)
            overrides.pop(app_name, None)
            archive["overrides"] = overrides

        cadence_buckets = maintenance.setdefault("cadence", {})
        policy_buckets = maintenance.setdefault("update_policy", {})
        for bucket, apps in cadence_buckets.items():
            if app_name in (apps or []):
                apps.remove(app_name)
        for bucket, apps in policy_buckets.items():
            if app_name in (apps or []):
                apps.remove(app_name)
        cadence_buckets.setdefault(cadence, [])
        if app_name not in cadence_buckets[cadence]:
            cadence_buckets[cadence].append(app_name)
            cadence_buckets[cadence].sort()
        policy_buckets.setdefault(update_policy, [])
        if app_name not in policy_buckets[update_policy]:
            policy_buckets[update_policy].append(app_name)
            policy_buckets[update_policy].sort()

        lifecycle = maintenance.setdefault("lifecycle", {})
        frozen = lifecycle.get("frozen") or []
        if app_name in frozen:
            frozen.remove(app_name)
        lifecycle["frozen"] = frozen

        if dry_run:
            actions["metadata_updated"] = True
            return actions

        shutil.move(str(source), str(target))
        _write_yaml(maintenance_path, maintenance)
        _write_yaml(archive_path, archive)
        actions["metadata_updated"] = True
        return actions


@app.command("list")
def list_apps(
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived apps"),
    scope: str | None = typer.Option(None, "--scope", help="Filter by scope: public | internal"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    output = collect_apps(include_archived=include_archived, scope=scope)

    if not as_json:
        table = Table("name", "status", "cadence", "update policy", "scope", "dockerfile", header_style="dim", box=box.SIMPLE)
        for item in output:
            table.add_row(
                item["name"],
                item["status"],
                item["cadence"],
                item["update_policy"],
                item["scope"],
                "yes" if item["dockerfile"] else "no",
            )
        Console().print(table)
        return

    print_output(output, as_json)
