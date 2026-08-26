from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import requests
import yaml

from libs.metadata import app_dir
from libs import remote
from libs.repo import repo_path


VAR_REF_RE = re.compile(r"\$([A-Z0-9_]+)")

DEFAULT_REQUIRED_CASES = (
    {"id": "compose-config", "type": "compose-config"},
    {"id": "container-up", "type": "container-up"},
)


def cases_path(app_name: str) -> Path:
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)
    return target / "tests" / "cases.yml"


def load_cases(app_name: str) -> dict:
    path = cases_path(app_name)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_env(app_name: str) -> dict:
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)
    env_path = target / ".env"
    if not env_path.exists():
        return {}

    raw = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        raw[key] = value

    resolved = dict(raw)
    for _ in range(5):
        changed = False
        for key, value in list(resolved.items()):
            new_value = VAR_REF_RE.sub(lambda m: resolved.get(m.group(1), m.group(0)), value)
            if new_value != value:
                resolved[key] = new_value
                changed = True
        if not changed:
            break
    return resolved


def _base_url(env: dict, explicit: str | None, ssh_host: str | None) -> str | None:
    if explicit:
        return explicit.rstrip("/")
    port = env.get("W9_HTTP_PORT_SET")
    if not port:
        return None
    resolved_ssh_host = ssh_host or (remote.ssh_host() if remote.default_target() == "remote" else None)
    if resolved_ssh_host:
        return f"http://{resolved_ssh_host}:{port}"
    return f"http://localhost:{port}"


def _run_subprocess(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def _run_remote(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def _remote_context(app_name: str, ssh_host: str | None, ssh_user: str | None, ssh_secret_path: str | None, deploy_root: str | None) -> dict | None:
    resolved_host = ssh_host or (remote.ssh_host() if remote.default_target() == "remote" else None)
    if not resolved_host:
        return None
    secret_path = remote.resolve_secret_path(ssh_secret_path)
    if not secret_path.exists():
        raise FileNotFoundError(f"SSH secret not found: {secret_path}")
    return {
        "host": resolved_host,
        "user": remote.ssh_user(ssh_user),
        "secret_path": secret_path,
        "app_target": f"{remote.deploy_root(deploy_root)}/{app_name}",
    }


def run_case(app_name: str, case: dict, env: dict, base_url: str | None, remote_ctx: dict | None) -> dict:
    target = app_dir(app_name)
    assert target is not None
    case_id = case.get("id") or case["type"]
    case_type = case["type"]

    if case_type == "compose-config":
        if remote_ctx:
            result = _run_remote(
                remote.ssh_base(remote_ctx["host"], remote_ctx["user"], remote_ctx["secret_path"])
                + [f"docker compose -f {remote_ctx['app_target']}/docker-compose.yml --env-file {remote_ctx['app_target']}/.env config --quiet"]
            )
        else:
            result = _run_subprocess([
                "docker", "compose", "-f", str(target / "docker-compose.yml"), "--env-file", str(target / ".env"), "config", "--quiet"
            ])
        return {"id": case_id, "ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}

    if case_type == "container-up":
        if remote_ctx:
            result = _run_remote(
                remote.ssh_base(remote_ctx["host"], remote_ctx["user"], remote_ctx["secret_path"])
                + ["docker ps --format '{{.Names}} {{.Status}}'"]
            )
        else:
            result = _run_subprocess(["docker", "ps", "--format", "{{.Names}} {{.Status}}"])
        container_id = env.get("W9_ID", app_name)
        line = next((line for line in result.stdout.splitlines() if line.split()[0].startswith(container_id)), "")
        return {"id": case_id, "ok": bool(line and "Up" in line), "stdout": line, "stderr": result.stderr}

    if case_type == "web-access":
        if not base_url:
            raise FileNotFoundError("web access requested but no base URL is available")
        path = case.get("path", "/")
        response = requests.get(f"{base_url}{path}", timeout=15, allow_redirects=True)
        expect = case.get("expect_status", [200])
        if isinstance(expect, int):
            expect = [expect]
        return {"id": case_id, "ok": response.status_code in expect, "status": response.status_code, "url": response.url}

    if case_type == "http-basic":
        if not base_url:
            raise FileNotFoundError("console login requested but no base URL is available")
        path = case.get("path", "/")
        user = env.get(case.get("username_env", "W9_LOGIN_USER"), "")
        password = env.get(case.get("password_env", "W9_LOGIN_PASSWORD"), "")
        response = requests.get(f"{base_url}{path}", timeout=15, allow_redirects=True, auth=(user, password))
        expect = case.get("expect_status", 200)
        if isinstance(expect, int):
            expect = [expect]
        return {"id": case_id, "ok": response.status_code in expect, "status": response.status_code, "url": response.url}

    if case_type == "script":
        script = target / "tests" / case["script"]
        if not script.exists():
            raise FileNotFoundError(f"missing test script: {script.relative_to(repo_path())}")
        run_env = {**env, "BASE_URL": base_url or "", "APP_NAME": app_name}
        result = subprocess.run(["bash", str(script)], check=False, capture_output=True, text=True, env=run_env)
        return {"id": case_id, "ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}

    raise ValueError(f"unsupported test type: {case_type}")


def _default_cases(env: dict, base_url: str | None) -> list[dict]:
    cases = [dict(item) for item in DEFAULT_REQUIRED_CASES]
    if base_url:
        cases.append({"id": "web-access", "type": "web-access", "path": "/", "expect_status": [200, 401, 403]})
    return cases


def run_app_tests(
    app_name: str,
    base_url: str | None = None,
    ssh_host: str | None = None,
    ssh_user: str | None = None,
    ssh_secret_path: str | None = None,
    deploy_root: str | None = None,
) -> dict:
    env = load_env(app_name)
    cases = load_cases(app_name)
    resolved_base_url = _base_url(env, base_url, ssh_host)
    remote_ctx = _remote_context(app_name, ssh_host, ssh_user, ssh_secret_path, deploy_root)

    skip_ids = {item["id"] for item in (cases.get("skip") or [])}
    results = []
    for case in _default_cases(env, resolved_base_url):
        if case["id"] in skip_ids:
            continue
        payload = run_case(app_name, case, env, resolved_base_url, remote_ctx)
        payload["group"] = "required"
        results.append(payload)

    for group in ("optional", "custom"):
        for case in cases.get(group) or []:
            payload = run_case(app_name, case, env, resolved_base_url, remote_ctx)
            payload["group"] = group
            results.append(payload)

    return {
        "app": app_name,
        "base_url": resolved_base_url,
        "target": "remote" if remote_ctx else "local",
        "ok": all(item.get("ok") for item in results),
        "results": results,
    }
