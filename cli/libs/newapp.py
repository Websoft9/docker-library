from __future__ import annotations

import json
import secrets
import string

import jsonschema
from jinja2 import Environment, FileSystemLoader

from libs.app import collect_apps
from libs.repo import repo_path
from libs.validate import check_app

SCHEMA_PATH = repo_path("metadata", "new-app.schema.json")
TEMPLATE_ROOT = repo_path("metadata", "templates", "new-app")
TEMPLATE_ENV = Environment(
    loader=FileSystemLoader(str(TEMPLATE_ROOT)),
    autoescape=False,
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def random_password(length: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_manifest() -> dict:
    return json.loads((TEMPLATE_ROOT / "manifest.json").read_text(encoding="utf-8"))


def validate_request(data: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(load_schema())
    errors = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "request"
        errors.append(f"{path}: {error.message}")
    return errors


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
    return TEMPLATE_ENV.get_template(name).render(**context)


def scaffold(
    name: str,
    trademark: str,
    version: str = "",
    repo: str = "",
    docs: dict | None = None,
    upstream: dict | None = None,
    dry_run: bool = False,
) -> dict:
    request = {
        "name": name,
        "trademark": trademark,
    }
    if version:
        request["version"] = version
    if repo:
        request["repo"] = repo
    if docs:
        request["docs"] = docs
    if upstream:
        request["upstream"] = upstream
    errors = validate_request(request)
    if errors:
        raise ValueError("; ".join(errors))
    existing = existing_app(name)
    if existing:
        raise FileExistsError(
            f"{name} already exists: status={existing['status']}, scope={existing['scope']}"
        )

    manifest = load_manifest()
    docs = docs or {}
    upstream = upstream or {}
    image_url = docs.get("image") or (tags_url(repo) if repo else "")
    target = repo_path("apps", name)

    context = {
        "name": name,
        "trademark": trademark,
        "version": version or "TODO",
        "repo": repo or "TODO",
        "image_url": image_url or "TODO",
        "releases_url": upstream.get("releases") or "",
        "compose_url": upstream.get("compose") or "",
        "compose_env_url": upstream.get("env") or "",
        "github_url": docs.get("github") or "",
        "install_url": docs.get("install") or "",
        "docs_json": json.dumps([url for url in (docs.get("github"), docs.get("install")) if url], ensure_ascii=False),
        "has_releases": bool(upstream.get("releases")),
        "has_compose": bool(upstream.get("compose")),
        "has_compose_env": bool(upstream.get("env")),
        "has_compose_group": bool(upstream.get("compose") or upstream.get("env")),
        "has_install_url": bool(docs.get("install")),
        "has_fork_url": bool(docs.get("github")),
        "power_password": random_password(),
    }
    files = {
        ".env": render_file(".env.tmpl", context),
        "docker-compose.yml": render_file("docker-compose.yml.tmpl", context),
        "variables.json": render_file("variables.json.tmpl", context) + "\n",
        "README.md": render_file("README.md.tmpl", context),
        "CHANGELOG.md": render_file("CHANGELOG.md.tmpl", context) + "\n",
        "src/.gitkeep": (TEMPLATE_ROOT / "src" / ".gitkeep").read_text(encoding="utf-8"),
    }

    payload = {
        "app": name,
        "trademark": trademark,
        "version": version or "TODO",
        "repo": repo or "TODO",
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
        "fill any missing upstream metadata in variables.json (releases, compose, env) when official sources exist",
        "design compose: volumes, healthcheck, db service and its version",
        "register new translatable W9_* keys in i18n/translation.json",
        "run libs gen-readme --app <app> after editing variables.json",
        "run the deploy-validation skill",
    ]
    return payload
