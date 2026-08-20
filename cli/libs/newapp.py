from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

from libs.app import collect_apps
from libs.repo import repo_path
from libs.validate import check_app

SCHEMA_PATH = repo_path("metadata", "new-app.schema.json")
TEMPLATE_ROOT = repo_path("metadata", "templates", "new-app")
BLOCK_RE = re.compile(r"```ya?ml\s*new-app-request\s*\n(.*?)```", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_manifest() -> dict:
    return json.loads((TEMPLATE_ROOT / "manifest.json").read_text(encoding="utf-8"))


def parse_issue_block(text: str) -> dict | None:
    match = BLOCK_RE.search(text)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def validate_request(data: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(load_schema())
    errors = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "request"
        errors.append(f"{path}: {error.message}")
    return errors


def read_issue_source(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8")


def existing_app(name: str) -> dict | None:
    for item in collect_apps(include_archived=True):
        if item["name"] == name:
            return item
    return None


def tags_url(repo: str) -> str:
    if "/" in repo and not repo.startswith(("http://", "https://")):
        return f"https://hub.docker.com/r/{repo}/tags"
    return repo


def render_file(name: str, context: dict) -> str:
    return (TEMPLATE_ROOT / name).read_text(encoding="utf-8").format(**context)


def scaffold(name: str, trademark: str, version: str, repo: str, docs: dict | None = None, dry_run: bool = False) -> dict:
    if not NAME_RE.match(name):
        raise ValueError(f"invalid app name: {name} (expected [a-z0-9][a-z0-9-]*)")
    if not version:
        raise ValueError("version is required; research first, then scaffold")
    if not repo:
        raise ValueError("repo is required; research the image first, then scaffold")
    existing = existing_app(name)
    if existing:
        raise FileExistsError(
            f"{name} already exists: status={existing['status']}, scope={existing['scope']}"
        )

    manifest = load_manifest()
    docs = docs or {}
    image_url = docs.get("image") or tags_url(repo)
    target = repo_path("apps", name)

    context = {
        "name": name,
        "trademark": trademark,
        "version": version,
        "repo": repo,
        "image_url": image_url,
        "github_url": docs.get("github") or "",
        "install_url": docs.get("install") or "",
        "docs_json": json.dumps([url for url in (docs.get("github"), docs.get("install")) if url], ensure_ascii=False),
    }
    files = {
        ".env": render_file(".env.tmpl", context),
        "docker-compose.yml": render_file("docker-compose.yml.tmpl", context),
        "variables.json": render_file("variables.json.tmpl", context) + "\n",
        "README.md": render_file("README.md.tmpl", context),
        "src/.gitkeep": (TEMPLATE_ROOT / "src" / ".gitkeep").read_text(encoding="utf-8"),
    }

    payload = {
        "app": name,
        "trademark": trademark,
        "version": version,
        "repo": repo,
        "files": manifest["generated_files"],
        "dry_run": dry_run,
    }

    if dry_run:
        return payload

    target.mkdir(parents=True, exist_ok=False)
    for relative, content in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    payload["check"] = check_app(name, gate="all")
    payload["todo"] = [
        "fill upstream metadata (compose, config sources) in variables.json",
        "design compose: volumes, healthcheck, db service and its version",
        "register new translatable W9_* keys in i18n/translation.json",
        "run libs check --app <app> and deployment validation",
    ]
    return payload
