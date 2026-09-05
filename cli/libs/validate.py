from __future__ import annotations

import json
import re
from pathlib import Path

import typer
import yaml

from libs.metadata import app_dir
from libs.output import print_output
from libs.repo import repo_path


app = typer.Typer(
    invoke_without_command=True,
    help="Validate one app",
    context_settings={"help_option_names": ["-h", "--help"]},
)

REQUIRED_FILES = [".env", "docker-compose.yml", "variables.json", "README.md", "CHANGELOG.md"]
TRANSLATABLE_ENV_RE = re.compile(r"^(W9_.*_SET|W9_LOGIN.*)$")
URL_CONFIG_REF_RE = re.compile(r"\$(?:\{)?W9_URL(?:\})?")
URL_AWARE_KEY_RE = re.compile(
    r"(^|_)(ROOT_URL|BASE_URL|SITE_URL|APP_URL|PUBLIC_URL|WEBAPP_URL|HOMEPAGE_URL|EXTERNAL_URL|"
    r"HOST|DOMAIN|SERVER_URL|PUBLISHEDSERVERURL|EXTERNALDOMAIN|EXTERNAL_HOST|PUBLIC_URI|WEBHOOK_URL)(_|$)",
    re.IGNORECASE,
)
DEPENDENCY_IMAGE_RE = re.compile(r"^(?P<repo>[^:@]+(?:/[^:@]+)*):(?P<tag>[^@\s]+)(?:@(?P<digest>sha256:[a-f0-9]+))?$")
PATCH_TAG_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-_][A-Za-z0-9._-]+)?$")
DEPENDENCY_TAG_HINT_RE = re.compile(r"(redis|postgres|postgresql|mysql|mariadb|pgvector)", re.IGNORECASE)


def _read_compose(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _structure_result(target: Path) -> dict:
    missing = [name for name in REQUIRED_FILES if not (target / name).exists()]
    missing_src = []
    compose_path = target / "docker-compose.yml"
    if compose_path.exists():
        compose = _read_compose(compose_path)
        services = compose.get("services") or {}
        for service in services.values():
            for volume in service.get("volumes", []) or []:
                if not isinstance(volume, str) or not volume.startswith("./src/"):
                    continue
                source = volume.split(":", 1)[0].replace("./", "")
                if not (target / source).exists():
                    missing_src.append(source)

    ok = not missing and not missing_src
    return {
        "ok": ok,
        "missing_files": missing,
        "missing_src": sorted(set(missing_src)),
    }


def _policy_result(target: Path) -> dict:
    env_path = target / ".env"
    compose_path = target / "docker-compose.yml"
    translation_path = repo_path("i18n", "translation.json")

    env_lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    env_keys = []
    env_map = {}
    for line in env_lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_keys.append(key)
        env_map[key] = value

    compose_text = compose_path.read_text(encoding="utf-8") if compose_path.exists() else ""
    compose = _read_compose(compose_path) if compose_path.exists() else {}
    translation = {}
    if translation_path.exists():
        translation = json.loads(translation_path.read_text(encoding="utf-8"))

    missing_translation = [key for key in env_keys if TRANSLATABLE_ENV_RE.match(key) and key not in translation]
    login_keys = [key for key in ("W9_LOGIN_USER", "W9_LOGIN_PASSWORD") if key in env_map]
    login_pair_ok = len(login_keys) in (0, 2)
    url_declared_ok = "W9_URL_REPLACE" not in env_map or "W9_URL" in env_map
    url_replace_required = any(
        not key.startswith("W9_") and URL_AWARE_KEY_RE.search(key) and URL_CONFIG_REF_RE.search(value)
        for key, value in env_map.items()
    ) or bool(URL_CONFIG_REF_RE.search(compose_text))
    url_replace_ok = True
    if "W9_URL_REPLACE" in env_map:
        url_replace_ok = bool(URL_CONFIG_REF_RE.search(compose_text)) or any(
            bool(URL_CONFIG_REF_RE.search(value)) for value in env_map.values()
        )
    url_replace_required_ok = True
    if url_replace_required:
        url_replace_required_ok = env_map.get("W9_URL_REPLACE", "").strip("'\"").lower() == "true"
    dependency_patch_tags = []
    for service_name, service in (compose.get("services") or {}).items():
        image = service.get("image")
        if not isinstance(image, str) or "$" in image:
            continue
        match = DEPENDENCY_IMAGE_RE.match(image.strip())
        if not match:
            continue
        repo = match.group("repo")
        tag = match.group("tag")
        if not DEPENDENCY_TAG_HINT_RE.search(repo):
            continue
        if PATCH_TAG_RE.match(tag):
            dependency_patch_tags.append({"service": service_name, "image": image})
    dependency_tag_policy_ok = not dependency_patch_tags

    ok = (
        not missing_translation
        and login_pair_ok
        and url_declared_ok
        and url_replace_ok
        and url_replace_required_ok
        and dependency_tag_policy_ok
    )
    return {
        "ok": ok,
        "missing_translation_keys": missing_translation,
        "login_pair_ok": login_pair_ok,
        "url_declared_ok": url_declared_ok,
        "url_replace_ok": url_replace_ok,
        "url_replace_required": url_replace_required,
        "url_replace_required_ok": url_replace_required_ok,
        "dependency_patch_tags": dependency_patch_tags,
        "dependency_tag_policy_ok": dependency_tag_policy_ok,
    }


def _version_result(target: Path) -> dict:
    """W9_VERSION (.env) must be declared in variables.json edition (community).

    Rule source: docs/image-tag-spec.md.
    Apps without variables.json, without W9_VERSION, or whose W9_VERSION is a
    floating alias (latest) are reported as not_applicable rather than failing.
    """
    env_path = target / ".env"
    variables_path = target / "variables.json"
    if not env_path.exists() or not variables_path.exists():
        return {"ok": True, "status": "not_applicable", "note": "missing .env or variables.json"}

    variables = json.loads(variables_path.read_text(encoding="utf-8"))
    declared = [
        str(v)
        for edition in variables.get("edition", [])
        if edition.get("dist") == "community"
        for v in edition.get("version", [])
    ]

    w9_version = None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or not line.startswith("W9_VERSION="):
            continue
        w9_version = line.split("=", 1)[1].strip().strip("'\"")
        break

    if not w9_version:
        return {"ok": True, "status": "not_applicable", "note": "W9_VERSION not found in .env"}

    if w9_version.lower() in ("latest", "main", "stable"):
        return {"ok": True, "status": "not_applicable", "note": f"W9_VERSION is a floating alias: {w9_version}"}

    found = w9_version in declared
    return {
        "ok": found,
        "status": "ok" if found else "mismatch",
        "w9_version": w9_version,
        "declared": sorted(declared),
    }


def _resolve_app_or_exit(app_name: str) -> Path:
    target = app_dir(app_name)
    if not target:
        raise typer.Exit(code=4)
    return target


def check_app(app_name: str, gate: str = "all") -> dict:
    target = _resolve_app_or_exit(app_name)
    structure = _structure_result(target)
    policy = _policy_result(target)
    version = _version_result(target)

    if gate == "structure":
        return {"app": app_name, "gate": gate, "result": structure, "ok": structure["ok"]}
    if gate == "policy":
        return {"app": app_name, "gate": gate, "result": policy, "ok": policy["ok"]}
    if gate == "version":
        return {"app": app_name, "gate": gate, "result": version, "ok": version["ok"]}

    return {
        "app": app_name,
        "structure": structure,
        "policy": policy,
        "version": version,
        "ok": structure["ok"] and policy["ok"],
    }


@app.callback()
def validate_all(
    ctx: typer.Context,
    app_name: str | None = typer.Option(None, "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    if ctx.invoked_subcommand:
        return
    if not app_name:
        typer.echo("Missing option '--app'.", err=True)
        raise typer.Exit(code=2)
    payload = check_app(app_name, gate="all")
    print_output(payload, as_json)
    if not payload["ok"]:
        raise typer.Exit(code=1)


@app.command()
def structure(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    payload = check_app(app_name, gate="structure")
    print_output(payload, as_json)
    if not payload["ok"]:
        raise typer.Exit(code=1)


@app.command()
def policy(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    payload = check_app(app_name, gate="policy")
    print_output(payload, as_json)
    if not payload["ok"]:
        raise typer.Exit(code=1)


@app.command()
def version(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    payload = check_app(app_name, gate="version")
    print_output(payload, as_json)
    if not payload["ok"]:
        raise typer.Exit(code=1)
