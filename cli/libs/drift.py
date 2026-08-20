from __future__ import annotations

from pathlib import Path

import yaml

from libs.http import get


COMPARE_KEYS = ["image", "ports", "volumes", "depends_on", "healthcheck", "command", "entrypoint"]


def parse_compose(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def normalize_service(service: dict) -> dict:
    return {key: service.get(key) for key in COMPARE_KEYS if key in service}


def normalized_services(compose: dict) -> dict:
    services = compose.get("services") or {}
    return {name: normalize_service(service) for name, service in services.items()}


def dependency_images(compose: dict) -> list[str]:
    images = []
    for service in (compose.get("services") or {}).values():
        image = service.get("image")
        if image:
            images.append(str(image))
    return sorted(set(images))


def fetch_upstream_compose(url: str) -> tuple[dict | None, str | None]:
    try:
        response = get(url)
        response.raise_for_status()
        return yaml.safe_load(response.text) or {}, None
    except Exception as error:
        return None, str(error)


def diff_services(local: dict, upstream: dict) -> dict:
    local_services = normalized_services(local)
    upstream_services = normalized_services(upstream)

    local_names = set(local_services)
    upstream_names = set(upstream_services)

    changed = {}
    for name in sorted(local_names & upstream_names):
        local_normalized = local_services[name]
        upstream_normalized = upstream_services[name]
        differences = {}
        for key in COMPARE_KEYS:
            if local_normalized.get(key) != upstream_normalized.get(key):
                differences[key] = {
                    "local": local_normalized.get(key),
                    "upstream": upstream_normalized.get(key),
                }
        if differences:
            changed[name] = differences

    return {
        "services_added": sorted(upstream_names - local_names),
        "services_removed": sorted(local_names - upstream_names),
        "services_changed": changed,
    }


def fetch_upstream_text(url: str) -> tuple[str | None, str | None]:
    try:
        response = get(url)
        response.raise_for_status()
        return response.text, None
    except Exception as error:
        return None, str(error)


def parse_env_text(text: str) -> dict:
    result = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def parse_env_file(path: Path) -> dict:
    if not path.exists():
        return {}
    return parse_env_text(path.read_text(encoding="utf-8"))


def diff_config(local_env: dict, upstream_env: dict) -> dict:
    local_keys = set(local_env)
    upstream_keys = set(upstream_env)

    changed = {}
    for key in sorted(local_keys & upstream_keys):
        if local_env.get(key) != upstream_env.get(key):
            changed[key] = {
                "local": local_env.get(key),
                "upstream": upstream_env.get(key),
            }

    url_login_changed = [
        key
        for key in changed
        if "URL" in key or key.startswith("W9_LOGIN") or "LOGIN" in key
    ]

    return {
        "keys_added": sorted(upstream_keys - local_keys),
        "keys_removed": sorted(local_keys - upstream_keys),
        "defaults_changed": changed,
        "url_login_keys_changed": url_login_changed,
    }
