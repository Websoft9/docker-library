from __future__ import annotations

import os
from pathlib import Path

import requests


PROXY_KEYS = ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY", "all_proxy", "ALL_PROXY")
REPO_CONFIG_PATH = Path(__file__).resolve().parent.parent / "proxy.conf"


def default_timeout() -> tuple[float, float]:
    value = os.getenv("LIBS_HTTP_TIMEOUT", "15")
    try:
        seconds = float(value)
    except ValueError:
        seconds = 15.0
    return (min(5.0, seconds), seconds)


def _read_proxy_file(path: Path) -> str | None:
    if path.exists():
        value = path.read_text(encoding="utf-8").strip()
        return value or None
    return None


def saved_proxy() -> str | None:
    return _read_proxy_file(REPO_CONFIG_PATH)


def save_proxy(url: str) -> None:
    REPO_CONFIG_PATH.write_text(url.strip(), encoding="utf-8")


def clear_proxy() -> None:
    if REPO_CONFIG_PATH.exists():
        REPO_CONFIG_PATH.unlink()


def detect_proxy() -> str | None:
    for key in PROXY_KEYS:
        value = os.environ.get(key)
        if value:
            return value
    return saved_proxy()


def normalize_proxy_env(proxy: str | None = None) -> str | None:
    value = proxy or detect_proxy()
    if not value:
        return None

    os.environ["http_proxy"] = value
    os.environ["https_proxy"] = value
    os.environ["all_proxy"] = value
    if (os.environ.get("no_proxy") or os.environ.get("NO_PROXY")) == "*":
        os.environ["no_proxy"] = ""
        os.environ["NO_PROXY"] = ""
    return value


def get(url: str, params: dict | None = None, timeout: tuple[float, float] | None = None, headers: dict | None = None):
    if timeout is None:
        timeout = default_timeout()
    return requests.get(url, params=params, timeout=timeout, headers=headers)
