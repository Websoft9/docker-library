from __future__ import annotations

import json

from libs import catalog
from libs.credentials import resolve_secret
from libs.repo import repo_path

CONTENTFUL_TOKEN_ENV = "CONTENTFUL_ACCESS_TOKEN"
SPACE_ID = "ffrhttfighww"
CONTENT_TYPE = "product"
CATALOG_CONTENT_TYPE = "catalog"
DEFAULT_DRAFTS_DIR = catalog.DEFAULT_CATALOG_DIR
DRAFT_FIELD_KEYS = catalog.CATALOG_FIELD_KEYS


def load_variables(app_name: str) -> dict:
    for root in ("apps", "archive/apps"):
        path = repo_path(root, app_name, "variables.json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"variables.json not found for app {app_name}")


def load_draft(app_name: str, drafts_dir: str) -> dict:
    return catalog.load_catalog(app_name, drafts_dir)


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


def find_catalog_entry(client, environment: str, category_key: str):
    try:
        entries = client.entries(SPACE_ID, environment).all(
            {"content_type": CATALOG_CONTENT_TYPE, "fields.key": category_key}
        )
        return entries[0] if entries else None
    except Exception:
        return None


def build_catalog_links(client, environment: str, bindings: list[dict]) -> list[dict]:
    links = []
    missing = []
    for binding in bindings:
        child_key = binding["childKey"]
        entry = find_catalog_entry(client, environment, child_key)
        if not entry:
            missing.append(child_key)
            continue
        entry_id = (getattr(entry, "sys", None) or {}).get("id")
        if not entry_id:
            missing.append(child_key)
            continue
        links.append({"sys": {"type": "Link", "linkType": "Entry", "id": entry_id}})
    if missing:
        joined = ", ".join(sorted(set(missing)))
        raise ValueError(f"missing Contentful catalog entries for keys: {joined}")
    return links


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


def update_entry_fields(entry, machine_fields: dict, draft_fields: dict, catalog_links: list[dict] | None = None) -> None:
    for key, value in {**machine_fields, **draft_fields}.items():
        if value is not None:
            entry.fields("en-US")[key] = value
    if catalog_links is not None:
        entry.fields("en-US")["catalog"] = catalog_links
    entry.save()
    entry.publish()


def _load_client(token: str | None = None, env_file: str | None = None):
    token = resolve_secret(CONTENTFUL_TOKEN_ENV, "contentful", token, env_file)
    if not token:
        raise FileNotFoundError(
            f"missing {CONTENTFUL_TOKEN_ENV}; set the env var, add .secrets/contentful.env, pass --env-file, or pass --token"
        )
    try:
        from contentful_management import Client
    except ImportError as error:
        raise FileNotFoundError("contentful_management is not installed; run: pip install contentful_management") from error
    return Client(token)


def sync_app(
    app_name: str,
    environment: str,
    drafts_dir: str,
    apply: bool,
    update_machine: bool,
    token: str | None = None,
    env_file: str | None = None,
) -> dict:
    variables = load_variables(app_name)
    draft = load_draft(app_name, drafts_dir)
    machine_fields = build_machine_fields(variables)
    draft_fields = build_draft_fields(draft)
    catalog_bindings = catalog.validate_catalog_bindings(draft, catalog.load_taxonomy()) if draft.get("catalogBindings") else []

    payload = {
        "app": app_name,
        "environment": environment,
        "dry_run": not apply,
        "machine_fields": machine_fields,
        "draft_fields": draft_fields,
        "catalog_bindings": catalog_bindings,
    }
    if not apply:
        try:
            client = _load_client(token, env_file)
        except FileNotFoundError:
            client = None
        if client is None:
            payload["action"] = "create"
            payload["exists_unknown"] = True
        else:
            existing = find_existing_entry(client, environment, app_name)
            payload["action"] = "update" if existing else "create"
            payload["exists"] = bool(existing)
        return payload

    client = _load_client(token, env_file)
    existing = find_existing_entry(client, environment, app_name)
    catalog_links = build_catalog_links(client, environment, catalog_bindings) if catalog_bindings else None
    if existing:
        if update_machine:
            update_machine_fields(existing, machine_fields)
            payload["action"] = "update-machine"
        else:
            update_entry_fields(existing, machine_fields, draft_fields, catalog_links)
            payload["action"] = "updated"
        payload["dry_run"] = False
        return payload

    fields = localized({**machine_fields, **draft_fields})
    if catalog_links is not None:
        fields["catalog"] = {"en-US": catalog_links}
    create_entry(client, environment, fields)
    payload["action"] = "created"
    payload["dry_run"] = False
    payload["fields"] = sorted(fields)
    return payload


def update_fields(
    app_name: str,
    environment: str,
    fields: dict,
    apply: bool,
    token: str | None = None,
    env_file: str | None = None,
) -> dict:
    payload = {
        "app": app_name,
        "environment": environment,
        "dry_run": not apply,
        "fields": {key: value for key, value in fields.items() if value is not None},
    }
    if not apply:
        payload["action"] = "update"
        return payload

    client = _load_client(token, env_file)
    existing = find_existing_entry(client, environment, app_name)
    if not existing:
        payload["action"] = "not-found"
        payload["dry_run"] = False
        return payload

    for key, value in fields.items():
        if value is not None:
            existing.fields("en-US")[key] = value
    existing.save()
    existing.publish()
    payload["action"] = "updated"
    payload["dry_run"] = False
    return payload
