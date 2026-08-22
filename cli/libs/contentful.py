from __future__ import annotations

import json
import os

CONTENTFUL_TOKEN_ENV = "CONTENTFUL_ACCESS_TOKEN"
SPACE_ID = "ffrhttfighww"
CONTENT_TYPE = "product"
DEFAULT_DRAFTS_DIR = "metadata/contentful-drafts"
DRAFT_FIELD_KEYS = ("trademark", "summary", "overview", "description", "websiteurl", "screenshots")


def load_variables(app_name: str) -> dict:
    from libs.repo import repo_path

    for root in ("apps", "archive/apps"):
        path = repo_path(root, app_name, "variables.json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"variables.json not found for app {app_name}")


def load_draft(app_name: str, drafts_dir: str) -> dict:
    from libs.repo import repo_path

    path = repo_path(drafts_dir, f"{app_name}.json")
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_machine_fields(variables: dict) -> dict:
    requirements = variables.get("requirements") or {}
    return {
        "key": variables.get("name"),
        "distribution": [
            {"key": edition.get("dist"), "value": edition.get("version", [])}
            for edition in variables.get("edition", [])
            if edition.get("dist")
        ],
        "vcpu": int(requirements.get("cpu", 1)),
        "memory": int(requirements.get("memory", 1)),
        "storage": int(requirements.get("disk", 1)),
        "production": bool(variables.get("release", False)),
    }


def build_draft_fields(draft: dict) -> dict:
    return {key: draft.get(key) for key in DRAFT_FIELD_KEYS if draft.get(key) is not None}


def localized(fields: dict) -> dict:
    return {key: {"en-US": value} for key, value in fields.items() if value is not None}


def find_existing_entry(client, environment: str, app_name: str):
    try:
        entries = client.entries(SPACE_ID, environment).all(
            {"content_type": CONTENT_TYPE, "fields.key": app_name}
        )
        return entries[0] if entries else None
    except Exception:
        return None


def create_entry(client, environment: str, fields: dict):
    entry = client.entries(SPACE_ID, environment).create(CONTENT_TYPE, fields)
    entry.publish()
    return entry


def update_machine_fields(entry, machine_fields: dict) -> None:
    for key, value in machine_fields.items():
        if value is not None:
            entry.fields("en-US")[key] = value
    entry.save()
    entry.publish()


def _load_client():
    token = os.getenv(CONTENTFUL_TOKEN_ENV)
    if not token:
        raise FileNotFoundError(f"missing {CONTENTFUL_TOKEN_ENV} environment variable")
    try:
        from contentful_management import Client
    except ImportError as error:
        raise FileNotFoundError("contentful_management is not installed; run: pip install contentful_management") from error
    return Client(token)


def sync_app(app_name: str, environment: str, drafts_dir: str, apply: bool, update_machine: bool) -> dict:
    variables = load_variables(app_name)
    draft = load_draft(app_name, drafts_dir)
    machine_fields = build_machine_fields(variables)
    draft_fields = build_draft_fields(draft)

    payload = {
        "app": app_name,
        "environment": environment,
        "dry_run": not apply,
        "machine_fields": machine_fields,
        "draft_fields": draft_fields,
    }
    if not apply:
        payload["action"] = "create"
        return payload

    client = _load_client()
    existing = find_existing_entry(client, environment, app_name)
    if existing:
        if update_machine:
            update_machine_fields(existing, machine_fields)
            payload["action"] = "update-machine"
        else:
            payload["action"] = "exists"
        payload["dry_run"] = False
        return payload

    fields = localized({**machine_fields, **draft_fields})
    create_entry(client, environment, fields)
    payload["action"] = "created"
    payload["dry_run"] = False
    payload["fields"] = sorted(fields)
    return payload
