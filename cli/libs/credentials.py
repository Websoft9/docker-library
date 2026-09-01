from __future__ import annotations

import os
from pathlib import Path

from libs.repo import repo_path


PROVIDER_FILES = {
    "contentful": ".secrets/contentful.env",
    "cloudflare": ".secrets/cloudflare.env",
    "dockerhub": ".secrets/dockerhub.env",
}


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip("'").strip('"')
    return data


def provider_env_path(provider: str) -> Path:
    relative = PROVIDER_FILES.get(provider)
    if not relative:
        raise ValueError(f"unsupported provider: {provider}")
    return repo_path(relative)


def load_provider_env(provider: str, env_file: str | None = None) -> dict[str, str]:
    if env_file:
        path = Path(env_file)
        if not path.is_absolute():
            path = repo_path(env_file)
        return _read_env_file(path)
    return _read_env_file(provider_env_path(provider))


def resolve_secret(name: str, provider: str, explicit: str | None = None, env_file: str | None = None) -> str | None:
    if explicit:
        return explicit
    if env_file:
        return load_provider_env(provider, env_file).get(name)
    env_value = os.getenv(name)
    if env_value:
        return env_value
    return load_provider_env(provider).get(name)
