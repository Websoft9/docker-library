from pathlib import Path

import yaml


ALLOWED_CADENCE = {"weekly", "monthly", "quarterly"}
ALLOWED_UPDATE_POLICY = {"patch-minor", "minor-only", "lts-only", "security-first", "manual-major"}


def app_roots():
    return [Path("apps"), Path("archive/apps")]


def known_apps():
    apps = set()
    for root in app_roots():
        if not root.exists():
            continue
        apps.update(path.name for path in root.iterdir() if path.is_dir())
    return apps


def load_maintenance_metadata():
    metadata_file = Path("metadata/maintenance.yaml")
    archive_file = Path("metadata/archive.yaml")
    if not metadata_file.exists():
        data = {
            "defaults": {},
            "cadence": {},
            "update_policy": {},
            "lifecycle": {},
        }

        if archive_file.exists():
            with open(archive_file, "r", encoding="utf-8") as file:
                archive_data = yaml.safe_load(file) or {}
            data.setdefault("lifecycle", {})["archived"] = resolve_archive_entries(archive_data)

        validate_maintenance_metadata(data)
        return data

    with open(metadata_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    if archive_file.exists():
        with open(archive_file, "r", encoding="utf-8") as file:
            archive_data = yaml.safe_load(file) or {}
        data.setdefault("lifecycle", {})["archived"] = resolve_archive_entries(archive_data)

    validate_maintenance_metadata(data)
    return data


def validate_maintenance_metadata(data):
    existing = known_apps()
    seen_cadence = {}
    seen_policy = {}

    for cadence, apps in (data.get("cadence") or {}).items():
        if cadence not in ALLOWED_CADENCE:
            raise ValueError(f"Unknown cadence bucket: {cadence}")
        for app in apps or []:
            if app not in existing:
                raise ValueError(f"Unknown app in cadence.{cadence}: {app}")
            previous = seen_cadence.get(app)
            if previous:
                raise ValueError(f"App listed in multiple cadence buckets: {app} ({previous}, {cadence})")
            seen_cadence[app] = cadence

    for policy, apps in (data.get("update_policy") or {}).items():
        if policy not in ALLOWED_UPDATE_POLICY:
            raise ValueError(f"Unknown update policy bucket: {policy}")
        for app in apps or []:
            if app not in existing:
                raise ValueError(f"Unknown app in update_policy.{policy}: {app}")
            previous = seen_policy.get(app)
            if previous:
                raise ValueError(f"App listed in multiple update policy buckets: {app} ({previous}, {policy})")
            seen_policy[app] = policy

    lifecycle = data.get("lifecycle") or {}
    frozen = set(lifecycle.get("frozen") or [])
    archived = set((lifecycle.get("archived") or {}).keys())

    for app in frozen | archived:
        if app not in existing:
            raise ValueError(f"Unknown app in lifecycle: {app}")

    overlap = frozen & archived
    if overlap:
        raise ValueError(f"Apps cannot be both frozen and archived: {sorted(overlap)}")

    illegal_cadence = archived & set(seen_cadence)
    if illegal_cadence:
        raise ValueError(f"Archived apps cannot have cadence entries: {sorted(illegal_cadence)}")

    illegal_policy = archived & set(seen_policy)
    if illegal_policy:
        raise ValueError(f"Archived apps cannot have update policy entries: {sorted(illegal_policy)}")


def resolve_app_metadata(metadata, app_name):
    resolved = dict(metadata.get("defaults") or {})

    for cadence, apps in (metadata.get("cadence") or {}).items():
        if app_name in (apps or []):
            resolved["cadence"] = cadence
            break

    for policy, apps in (metadata.get("update_policy") or {}).items():
        if app_name in (apps or []):
            resolved["update_policy"] = policy
            break

    lifecycle = metadata.get("lifecycle") or {}
    if app_name in (lifecycle.get("frozen") or []):
        resolved["status"] = "frozen"

    archived = lifecycle.get("archived") or {}
    if app_name in archived:
        resolved["status"] = "archived"
        resolved["cadence"] = "none"
        resolved["update_policy"] = "none"
        resolved.update(archived[app_name] or {})

    return resolved


def contentful_override(metadata, app_name):
    return resolve_app_metadata(metadata, app_name).get("contentful") or {}


def resolve_archive_entries(data):
    defaults = data.get("defaults") or {}
    apps = data.get("apps") or []
    overrides = data.get("overrides") or {}
    resolved = {}

    for app in apps:
        resolved[app] = dict(defaults)
        resolved[app].update(overrides.get(app) or {})

    for app, extra in overrides.items():
        if app not in resolved:
            resolved[app] = dict(defaults)
            resolved[app].update(extra or {})

    return resolved
