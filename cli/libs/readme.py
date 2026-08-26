from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from libs.metadata import app_dir
from libs.repo import repo_path

TEMPLATE_ROOT = repo_path("metadata", "templates")

GUIDE_START = "<!-- W9_GUIDE_START -->"
GUIDE_END = "<!-- W9_GUIDE_END -->"
TROUBLE_START = "<!-- W9_TROUBLESHOOT_START -->"
TROUBLE_END = "<!-- W9_TROUBLESHOOT_END -->"
CHANGELOG_START = "<!-- W9_CHANGELOG_START -->"
CHANGELOG_END = "<!-- W9_CHANGELOG_END -->"
NOTE_START = "<!-- W9_NOTE_START -->"
NOTE_END = "<!-- W9_NOTE_END -->"
PORT_LINE_RE = re.compile(r'^\s*-\s*"?\$?(?P<var>[A-Z0-9_]+)?:(?P<cport>\d+)"?\s*(?:#\s*(?P<note>.*))?$')
VOLUME_LINE_RE = re.compile(r'^\s*-\s*(?P<src>[\w.\/]+):(?P<dst>\/\S+?)(?::ro)?$')


def _extract_block(text: str, start: str, end: str) -> str:
    s = text.find(start)
    e = text.find(end)
    if s == -1 or e == -1 or e <= s:
        return ""
    return text[s + len(start):e].strip("\n")


def _compose_ports(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        match = PORT_LINE_RE.match(line)
        if not match:
            continue
        cport = match.group("cport")
        note = (match.group("note") or match.group("var") or cport).strip()
        rows.append({"purpose": note, "port": cport})
    return rows


def _compose_volumes(text: str) -> tuple[list[dict], list[dict]]:
    data_dirs = []
    config_overrides = []
    for line in text.splitlines():
        match = VOLUME_LINE_RE.match(line)
        if not match:
            continue
        src, dst = match.group("src"), match.group("dst")
        if src.startswith("./src/"):
            config_overrides.append({"source": src, "target": dst})
        else:
            data_dirs.append({"volume": src, "path": dst})
    return data_dirs, config_overrides


def _references(variables: dict) -> list[dict]:
    refs = []
    upstream = variables.get("upstream") or {}
    image = upstream.get("image")
    if image:
        refs.append({"label": "Docker Hub image", "url": image})
    releases = upstream.get("releases")
    if releases:
        refs.append({"label": "Releases", "url": releases})
    for doc in upstream.get("docs") or []:
        label = "GitHub docs" if "github.com" in doc else "Official docs"
        refs.append({"label": label, "url": doc})
    return refs


def _default_guide(admin_url: str | None, trademark: str) -> str:
    lines = ["### Usage", ""]
    lines.append(f"1. Make sure you are signed in to the {trademark} admin console.")
    lines.append("2. Try a core feature.")
    lines.extend([
        "",
        "### Change Password",
        "",
        "1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.",
        "2. Update the password in `.env` and save.",
        "3. Rebuild the app.",
    ])
    return "\n".join(lines)


def _default_troubleshooting() -> str:
    return "## Troubleshooting\n\n**App fails to start?**\n- Check `docker compose logs`.\n\n**Port not reachable?**\n- Ensure the firewall / security group allows the port." 


def _default_changelog(target: Path) -> str:
    changelog_path = target / "CHANGELOG.md"
    if changelog_path.exists():
        text = changelog_path.read_text(encoding="utf-8").strip()
        if text:
            return text
    return "首次发布。"


def _first_startup_only_note(variables: dict) -> str:
    names = (variables.get("env") or {}).get("first_startup_only") or []
    if not names:
        return ""
    joined = ", ".join(f"`{name}`" for name in names)
    return (
        f"Note: {joined} take effect on first startup only; changing them after deployment "
        "may not take effect until the app is re-initialized."
    )


def render_readme(app_name: str) -> dict:
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)

    variables_path = target / "variables.json"
    if not variables_path.exists():
        raise FileNotFoundError(f"{app_name}/variables.json")

    variables = json.loads(variables_path.read_text(encoding="utf-8"))
    readme_path = target / "README.md"
    existing = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

    compose_text = ""
    compose_path = target / "docker-compose.yml"
    if compose_path.exists():
        compose_text = compose_path.read_text(encoding="utf-8")

    data_dirs, config_overrides = _compose_volumes(compose_text)
    ports = _compose_ports(compose_text)
    admin_port = next((p["port"] for p in ports if p["purpose"] in ("Web Console", "Admin", "Console")), None)
    admin_url = f"http://<host>:{admin_port}/admin" if admin_port else None

    context = dict(variables)
    context["ports"] = ports
    context["data_dirs"] = data_dirs
    context["config_overrides"] = config_overrides
    context["references"] = _references(variables)
    context["image_url"] = (variables.get("upstream") or {}).get("image") or ""
    context["has_latest"] = any("latest" in (ed.get("version") or []) for ed in variables.get("edition") or [])
    context["guide"] = _extract_block(existing, GUIDE_START, GUIDE_END) or _default_guide(admin_url, variables.get("trademark", app_name))
    context["troubleshooting"] = _extract_block(existing, TROUBLE_START, TROUBLE_END) or _default_troubleshooting()
    context["changelog"] = _extract_block(existing, CHANGELOG_START, CHANGELOG_END) or _default_changelog(target)
    context["config_note"] = _extract_block(existing, NOTE_START, NOTE_END)
    context["first_startup_only_note"] = _first_startup_only_note(variables)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_ROOT)), keep_trailing_newline=True)
    rendered = env.get_template("readme.jinja2").render(**context)

    readme_path.write_text(rendered, encoding="utf-8")

    return {
        "app": app_name,
        "path": str(readme_path.relative_to(repo_path())),
        "bytes": len(rendered.encode("utf-8")),
    }
