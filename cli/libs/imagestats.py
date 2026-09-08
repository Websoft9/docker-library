from __future__ import annotations

import re
from pathlib import Path

import yaml

from libs.repo import repo_path


DOCKERHUB_ALIASES = {"docker.io", "index.docker.io", "registry-1.docker.io"}
DOCKERHUB_DISPLAY = "docker.io"

_ENV_VAR_RE = re.compile(r"\$(\{([A-Za-z_][A-Za-z0-9_]*)([^}]*)\}|\b([A-Za-z_][A-Za-z0-9_]*))")
_KEY_VALUE_RE = re.compile(r"^(\s*)([A-Za-z0-9_.-]+)\s*:\s*(.*?)\s*$")


def parse_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        env[key.strip()] = value
    return env


def expand_env(value: str, env: dict[str, str]) -> tuple[str, list[str]]:
    unresolved: list[str] = []

    def replace(match: re.Match) -> str:
        name = match.group(2) or match.group(4)
        if name in env:
            return env[name]
        rest = match.group(3) or ""
        if rest.startswith(":-") and len(rest) > 2:
            return rest[2:]
        if rest.startswith("-") and len(rest) > 1:
            return rest[1:]
        unresolved.append(name)
        return match.group(0)

    return _ENV_VAR_RE.sub(replace, value), unresolved


def parse_image_ref(value: str) -> tuple[str, str] | None:
    """Return (canonical_host, repository_path) without tag/digest, or None when unparseable."""
    reference = value.strip()
    if not reference or " " in reference or "{{" in reference:
        return None
    if "@" in reference:
        reference = reference.split("@", 1)[0]

    host = DOCKERHUB_DISPLAY
    rest = reference
    slash = rest.find("/")
    if slash != -1:
        first = rest[:slash]
        if "." in first or ":" in first or first == "localhost":
            host = first
            rest = rest[slash + 1:]

    if ":" in rest:
        head, separator, tag = rest.rpartition(":")
        if separator and tag and "/" not in tag:
            rest = head

    rest = rest.strip("/")
    if not rest:
        return None
    if host.lower() in DOCKERHUB_ALIASES:
        host = DOCKERHUB_DISPLAY
        if rest.startswith("library/"):
            rest = rest[len("library/"):]
    if not rest or rest.startswith("/") or rest.endswith(":"):
        return None
    return host, rest


def is_official_image(host: str, path: str) -> bool:
    return host == DOCKERHUB_DISPLAY and "/" not in path


def load_compose(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _template_image_refs(path: Path) -> list[tuple[str, bool]] | None:
    """Best-effort scan for compose files that are Go-template flavored and not YAML-parseable.

    Only `image:`/`build:` keys under a top-level `services:` block are considered.
    Returns [(image, is_locally_built), ...] or None when the file has no parseable services block.
    """
    lines = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("{{/*") and stripped.endswith("*/}}"):
            continue
        match = _KEY_VALUE_RE.match(raw_line)
        if not match:
            continue
        indent = len(match.group(1))
        key = match.group(2)
        value = match.group(3).strip()
        if " #" in value:
            value = value.split(" #", 1)[0].strip()
        lines.append((indent, key, value))

    services_index = next(
        (index for index, (_, key, _) in enumerate(lines) if key == "services"),
        None,
    )
    if services_index is None:
        return None
    services_indent = lines[services_index][0]

    owner_indent: int | None = None
    owners: list[dict] = []
    current: dict | None = None
    for indent, key, value in lines[services_index + 1:]:
        if indent <= services_indent:
            break
        if owner_indent is None:
            owner_indent = indent
        if indent == owner_indent:
            current = {"image": None, "build": False}
            owners.append(current)
            continue
        if current is None:
            continue
        if key == "image":
            current["image"] = value
        elif key == "build":
            current["build"] = True

    refs = [(owner["image"], owner["build"]) for owner in owners if owner["image"]]
    return refs or None


def _collect_refs(app_dir: Path) -> tuple[list[dict], str | None]:
    """Return (records, warning). Each record: {image, local}."""
    compose_path = app_dir / "docker-compose.yml"
    if not compose_path.exists():
        return [], None

    compose = load_compose(compose_path)
    records: list[dict] = []
    warning: str | None = None

    if compose is not None:
        for service in (compose.get("services") or {}).values():
            if not isinstance(service, dict):
                continue
            image = service.get("image")
            if not isinstance(image, str) or not image:
                continue
            records.append({"image": image, "local": bool(service.get("build"))})
    else:
        refs = _template_image_refs(compose_path)
        if refs is None:
            warning = "compose could not be parsed and has no recognizable services block"
            return [], warning
        records = [{"image": image, "local": local} for image, local in refs]
        warning = "compose is a template; scanned image lines under services"

    return records, warning


def _app_dirs(include_archived: bool) -> list[Path]:
    dirs = []
    for root in (repo_path("apps"),):
        if root.exists():
            dirs.extend(sorted(path for path in root.iterdir() if path.is_dir()))
    if include_archived:
        archive_root = repo_path("archive", "apps")
        if archive_root.exists():
            dirs.extend(sorted(path for path in archive_root.iterdir() if path.is_dir()))
    return dirs


def compute_stats(
    app_filter: str | None = None,
    include_archived: bool = False,
) -> dict:
    """Aggregate distinct image repositories referenced across app compose files.

    Classification: a Docker official image lives on Docker Hub and has a single-segment
    repository path (no user namespace), e.g. `redis` vs `bitnami/wordpress` or `ghcr.io/x/y`.
    Images built locally (a service with `build:`) are reported but excluded from the counts.
    """
    scanned: list[str] = []
    skipped: list[dict] = []
    unresolved: list[dict] = []
    local_built = 0
    references = 0
    per_image: dict[tuple[str, str], dict] = {}
    app_names = [path.name for path in _app_dirs(include_archived)]
    if app_filter:
        if app_filter not in app_names:
            raise FileNotFoundError(app_filter)
        app_names = [app_filter]

    for name in app_names:
        app_dir = repo_path("apps", name)
        if not app_dir.exists():
            app_dir = repo_path("archive", "apps", name)
        records, warning = _collect_refs(app_dir)
        if warning:
            skipped.append({"app": name, "reason": warning})
            if not records:
                continue
        scanned.append(name)
        env = parse_env_file(app_dir / ".env")
        for record in records:
            raw = record["image"]
            if record["local"]:
                local_built += 1
                continue
            expanded, names = expand_env(raw, env)
            if names:
                unresolved.append({"app": name, "image": raw, "variables": sorted(set(names))})
                continue
            parsed = parse_image_ref(expanded)
            if parsed is None:
                unresolved.append({"app": name, "image": raw, "variables": []})
                continue
            host, path = parsed
            references += 1
            key = (host, path)
            if key not in per_image:
                per_image[key] = {"host": host, "path": path, "app": name}

    total = len(per_image)

    dockerio_images = sum(1 for host, _ in per_image if host == DOCKERHUB_DISPLAY)
    docker_official_images = sum(1 for host, path in per_image if is_official_image(host, path))
    non_dockerio_images = total - dockerio_images

    registries: dict[str, int] = {}
    for host, _ in per_image:
        if host == DOCKERHUB_DISPLAY:
            continue
        registries[host] = registries.get(host, 0) + 1

    return {
        "scanned_apps": scanned,
        "skipped_apps": skipped,
        "references": references,
        "locally_built_excluded": local_built,
        "unresolved": unresolved,
        "unique_images": total,
        "dockerio_images": dockerio_images,
        "docker_official_images": docker_official_images,
        "dockerio_non_official_images": dockerio_images - docker_official_images,
        "docker_official_percent": round(100.0 * docker_official_images / dockerio_images, 1)
        if dockerio_images
        else 0.0,
        "non_dockerio_images": non_dockerio_images,
        "registries": sorted(
            ({"registry": host, "images": count} for host, count in registries.items()),
            key=lambda item: (-item["images"], item["registry"]),
        ),
    }
