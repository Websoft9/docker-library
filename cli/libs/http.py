from __future__ import annotations

import json
import os
import shlex
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

import requests


PROXY_KEYS = ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY", "all_proxy", "ALL_PROXY")
REPO_CONFIG_PATH = Path(__file__).resolve().parent.parent / "proxy.conf"
_REMOTE_ONLY = False
_LOCAL_UNAVAILABLE = False
_REMOTE_UNAVAILABLE = False
_NETWORK_DEADLINE: float | None = None
_NETWORK_LAST_ERROR = ""
_NETWORK_STATS = {
    "local_probe_attempts": 0,
    "local_requests": 0,
    "remote_attempts": 0,
    "remote_retries": 0,
    "local_unavailable": False,
    "remote_unavailable": False,
}


def reset_network_state(deadline_seconds: float | None = None) -> None:
    """Reset per-command network state and optionally set a hard deadline."""
    global _LOCAL_UNAVAILABLE, _REMOTE_ONLY, _REMOTE_UNAVAILABLE, _NETWORK_DEADLINE, _NETWORK_STATS, _NETWORK_LAST_ERROR
    _REMOTE_ONLY = False
    _LOCAL_UNAVAILABLE = False
    _REMOTE_UNAVAILABLE = False
    _NETWORK_DEADLINE = time.monotonic() + deadline_seconds if deadline_seconds is not None else None
    _NETWORK_LAST_ERROR = ""
    _NETWORK_STATS = {
        "local_probe_attempts": 0,
        "local_requests": 0,
        "remote_attempts": 0,
        "remote_retries": 0,
        "local_unavailable": False,
        "remote_unavailable": False,
    }


def network_snapshot() -> dict:
    remaining = None if _NETWORK_DEADLINE is None else max(0, int(_NETWORK_DEADLINE - time.monotonic()))
    if _REMOTE_ONLY:
        path = "remote"
    elif _REMOTE_UNAVAILABLE:
        path = "unavailable"
    elif _LOCAL_UNAVAILABLE:
        path = "local-failed"
    else:
        path = "local"
    return {**_NETWORK_STATS, "path": path, "deadline_remaining_seconds": remaining}


def _remaining_budget() -> float | None:
    if _NETWORK_DEADLINE is None:
        return None
    return max(0.0, _NETWORK_DEADLINE - time.monotonic())


def _bounded_timeout(timeout: tuple[float, float] | None) -> tuple[float, float] | None:
    remaining = _remaining_budget()
    if remaining is None:
        return timeout
    if remaining <= 0:
        return (0.1, 0.1)
    base = timeout or default_timeout()
    # Version discovery uses a separate bounded remote fallback. Keep one
    # stalled local request from consuming the entire command budget.
    base = (min(base[0], 2.0), min(base[1], 2.0))
    return (min(base[0], remaining), min(base[1], remaining))


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


@dataclass(frozen=True)
class Reachability:
    """Result of a fast reachability probe.

    Any HTTP response (including 4xx/5xx) counts as reachable: it proves the
    host is routable and an HTTP server answered. Timeouts and connection
    errors count as unreachable.
    """

    ok: bool
    url: str
    attempts: int
    elapsed_ms: int
    status: int | None = None
    error: str | None = None


def probe_url(
    url: str,
    *,
    timeout: float = 2.0,
    retries: int = 2,
) -> Reachability:
    """Probe a URL with a hard 2s per-attempt budget and at most 2 retries.

    The default worst case is 3 attempts x 2s. Do not raise this default in
    automation: if the local path is blocked, callers should switch to the
    remote-egress fallback instead of waiting for a long HTTP timeout.
    """
    attempts_allowed = max(1, retries + 1)
    started = time.monotonic()
    last_error = None
    status = None
    for attempt in range(1, attempts_allowed + 1):
        try:
            response = requests.get(
                url,
                timeout=(timeout, timeout),
                stream=True,
                allow_redirects=True,
            )
            status = response.status_code
            response.close()
            return Reachability(
                ok=True,
                url=url,
                attempts=attempt,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                status=status,
            )
        except Exception as error:  # requests wraps DNS/proxy/TLS/timeout errors
            last_error = str(error)
            if attempt < attempts_allowed:
                time.sleep(0.05)
    return Reachability(
        ok=False,
        url=url,
        attempts=attempts_allowed,
        elapsed_ms=int((time.monotonic() - started) * 1000),
        status=status,
        error=last_error,
    )


def remote_get_json(url: str, params: dict | None, headers: dict | None) -> tuple[object | None, dict | None, str | None]:
    # Import lazily so http.py stays usable without a remote profile.
    from libs import remote

    global _REMOTE_UNAVAILABLE, _NETWORK_STATS, _NETWORK_LAST_ERROR
    if _REMOTE_UNAVAILABLE:
        return None, None, _NETWORK_LAST_ERROR or "remote egress unavailable after retry budget was exhausted"

    remaining = _remaining_budget()
    if remaining is not None and remaining <= 0:
        _REMOTE_UNAVAILABLE = True
        _NETWORK_STATS["remote_unavailable"] = True
        return None, None, "network scan deadline exceeded"

    host = remote.ssh_host()
    if not host:
        _REMOTE_UNAVAILABLE = True
        _NETWORK_STATS["remote_unavailable"] = True
        return None, None, "local network unreachable and no remote SSH host configured"
    secret_path = remote.resolve_secret_path()
    if not secret_path.exists():
        _REMOTE_UNAVAILABLE = True
        _NETWORK_STATS["remote_unavailable"] = True
        return None, None, f"local network unreachable and SSH secret not found: {secret_path}"

    target = url
    if params:
        target = f"{target}{'&' if '?' in target else '?'}{urlencode(params)}"
    # Keep the remote fallback bounded as well; a blocked local path should not
    # turn version discovery into a long retry cycle on the remote host.
    attempts = 2
    last_error = "remote fetch failed"
    for attempt in range(attempts):
        remaining = _remaining_budget()
        if remaining is not None and remaining <= 0:
            break
        curl_timeout = min(4.0, remaining) if remaining is not None else 4.0
        parts = ["curl", "-fsSL", "--connect-timeout", "2", "--max-time", str(max(1, int(curl_timeout)))]
        for key, value in (headers or {}).items():
            parts.extend(["-H", f"{key}: {value}"])
        parts.append(target)
        script = " ".join(shlex.quote(part) for part in parts)
        _NETWORK_STATS["remote_attempts"] += 1
        connect_timeout = min(3, max(1, int(remaining))) if remaining is not None else 3
        result = remote.run_ssh(host, remote.ssh_user(), secret_path, script, connect_timeout=connect_timeout)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout), {}, None
            except json.JSONDecodeError as error:
                last_error = f"remote response was not JSON: {error}"
        else:
            last_error = (result.stderr or result.stdout or "remote fetch failed").strip()
        if attempt == 0:
            _NETWORK_STATS["remote_retries"] += 1

    _REMOTE_UNAVAILABLE = True
    _NETWORK_STATS["remote_unavailable"] = True
    _NETWORK_LAST_ERROR = last_error
    return None, None, last_error


def get_json_with_fallback(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    *,
    timeout: tuple[float, float] | None = None,
) -> tuple[object | None, dict | None, str | None]:
    """Fetch JSON locally, falling back to the configured remote host's egress.

    The local path gets one fast probe (2s x at most 3 attempts). Only network
    failures trigger the remote fallback; HTTP 4xx/5xx responses are returned to
    the caller as normal responses so it can apply endpoint-specific handling.
    After one successful remote fallback, later calls in the same process skip
    the local probe and go straight to the remote path.
    """
    global _LOCAL_UNAVAILABLE, _REMOTE_ONLY, _REMOTE_UNAVAILABLE, _NETWORK_STATS, _NETWORK_LAST_ERROR

    remaining = _remaining_budget()
    if remaining is not None and remaining <= 0:
        _LOCAL_UNAVAILABLE = True
        _REMOTE_UNAVAILABLE = True
        _NETWORK_STATS["local_unavailable"] = True
        _NETWORK_STATS["remote_unavailable"] = True
        return None, None, "network scan deadline exceeded"

    if not _REMOTE_ONLY and not _LOCAL_UNAVAILABLE and not _REMOTE_UNAVAILABLE:
        probe_timeout = min(2.0, remaining) if remaining is not None else 2.0
        probe_retries = 0 if _NETWORK_DEADLINE is not None else 2
        probe = probe_url(url, timeout=max(0.1, probe_timeout), retries=probe_retries)
        _NETWORK_STATS["local_probe_attempts"] += probe.attempts
        if probe.ok:
            try:
                _NETWORK_STATS["local_requests"] += 1
                response = get(url, params, timeout=_bounded_timeout(timeout), headers=headers)
                if response.status_code == 429:
                    remaining = _remaining_budget()
                    if remaining is not None:
                        time.sleep(min(1, remaining))
                    else:
                        time.sleep(1)
                    response = get(url, params, timeout=_bounded_timeout(timeout), headers=headers)
                response.raise_for_status()
                return response.json(), dict(response.headers), None
            except Exception as error:
                _LOCAL_UNAVAILABLE = True
                _NETWORK_STATS["local_unavailable"] = True
                local_error = str(error)
        else:
            _LOCAL_UNAVAILABLE = True
            _NETWORK_STATS["local_unavailable"] = True
            local_error = probe.error or "local network probe failed"
    else:
        local_error = "local network path unavailable"

    if _REMOTE_UNAVAILABLE:
        return None, None, _NETWORK_LAST_ERROR or "remote egress unavailable after retry budget was exhausted"

    data, response_headers, error = remote_get_json(url, params, headers)
    if not error:
        _REMOTE_ONLY = True
    else:
        _REMOTE_UNAVAILABLE = True
        _NETWORK_STATS["remote_unavailable"] = True
        _NETWORK_LAST_ERROR = error
    return data, response_headers, error
