from __future__ import annotations

import re
from pathlib import Path

import typer
import yaml

from cli.metadata import app_dir
from cli.output import print_output

app = typer.Typer(
    invoke_without_command=True,
    help="Validate one app",
    context_settings={"help_option_names": ["-h", "--help"]},
)

REQUIRED_FILES = [".env", "docker-compose.yml", "variables.json", "README.md"]
TRANSLATABLE_ENV_RE = re.compile(r"^(W9_.*_SET|W9_LOGIN.*)$")


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
    translation_path = Path("i18n/translation.json")

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
    translation = {}
    if translation_path.exists():
        import json

        translation = json.loads(translation_path.read_text(encoding="utf-8"))

    missing_translation = [key for key in env_keys if TRANSLATABLE_ENV_RE.match(key) and key not in translation]
    login_keys = [key for key in ("W9_LOGIN_USER", "W9_LOGIN_PASSWORD") if key in env_map]
    login_pair_ok = len(login_keys) in (0, 2)
    url_replace_ok = True
    if "W9_URL_REPLACE" in env_map:
        url_replace_ok = "$W9_URL" in compose_text or any("$W9_URL" in value for value in env_map.values())

    ok = not missing_translation and login_pair_ok and url_replace_ok
    return {
        "ok": ok,
        "missing_translation_keys": missing_translation,
        "login_pair_ok": login_pair_ok,
        "url_replace_ok": url_replace_ok,
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

    if gate == "structure":
        return {"app": app_name, "gate": gate, "result": structure, "ok": structure["ok"]}
    if gate == "policy":
        return {"app": app_name, "gate": gate, "result": policy, "ok": policy["ok"]}

    return {
        "app": app_name,
        "structure": structure,
        "policy": policy,
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
