from __future__ import annotations

import json
import re
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

import requests
import yaml

from libs.metadata import app_dir
from libs import remote
from libs.repo import repo_path


VAR_REF_RE = re.compile(r"\$([A-Z0-9_]+)")
ProgressWriter = Callable[[str], None]

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


def load_compose(app_name: str) -> dict:
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)
    compose_path = target / "docker-compose.yml"
    if not compose_path.exists():
        return {}
    return yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}


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
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
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
    return remote.run_command(command)


def _run_remote(command: list[str]) -> subprocess.CompletedProcess:
    return remote.run_command(command)


def _announce(progress: ProgressWriter | None, index: int, total: int, message: str) -> None:
    if progress:
        progress(f"[{index}/{total}] {message}")


def _request_case(case_id: str, request: Callable[[], requests.Response], expect: int | list[int]) -> dict:
    if isinstance(expect, int):
        expect = [expect]
    try:
        response = request()
    except requests.RequestException as error:
        return {"id": case_id, "ok": False, "error": str(error)}
    return {"id": case_id, "ok": response.status_code in expect, "status": response.status_code, "url": response.url}


def _emit_case_detail(progress: ProgressWriter | None, payload: dict) -> None:
    if not progress:
        return
    if payload.get("stdout") and "health" not in payload:
        progress(str(payload["stdout"]).rstrip())
    if payload.get("stderr"):
        progress(str(payload["stderr"]).rstrip())
    if payload.get("error"):
        progress(str(payload["error"]))
    if "status" in payload or "url" in payload:
        parts = []
        if "status" in payload:
            parts.append(f"status={payload['status']}")
        if payload.get("health"):
            parts.append(f"health={payload['health']}")
        if payload.get("url"):
            parts.append(f"url={payload['url']}")
        if parts:
            progress(" ".join(parts))


def _main_service_name(app_name: str, compose: dict, env: dict) -> str | None:
    services = compose.get("services") or {}
    if not services:
        return None
    container_id = env.get("W9_ID", app_name)
    for name, service in services.items():
        container_name = str((service or {}).get("container_name") or "")
        if container_name == "$W9_ID" or container_name == "${W9_ID}" or container_name == container_id:
            return name
    if app_name in services:
        return app_name
    return next(iter(services))


def _service_has_healthcheck(compose: dict, service_name: str | None) -> bool:
    if not service_name:
        return False
    service = (compose.get("services") or {}).get(service_name) or {}
    return bool(service.get("healthcheck"))


def _container_name_prefix(env: dict, app_name: str) -> str:
    return env.get("W9_ID", app_name)


def _select_container_line(stdout: str, container_id: str) -> str:
    lines = [line for line in stdout.splitlines() if line.split()]
    exact = next((line for line in lines if line.split()[0] == container_id), "")
    if exact:
        return exact
    return next((line for line in lines if line.split()[0].startswith(container_id)), "")


def _inspect_state(stdout: str) -> tuple[str | None, str | None]:
    try:
        payload = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        return None, None
    if not payload:
        return None, None
    state = payload if isinstance(payload, dict) else (payload[0].get("State") if payload else {})
    return state.get("Status"), state.get("Health", {}).get("Status")


def _wait_for(wait_timeout: int, wait_interval: int, attempt: Callable[[], dict], retry_when: Callable[[dict], bool]) -> dict:
    start = time.monotonic()
    last = attempt()
    while retry_when(last) and (time.monotonic() - start) < wait_timeout:
        time.sleep(wait_interval)
        last = attempt()
    return last


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


def _run_remote_script(remote_ctx: dict, script: str) -> subprocess.CompletedProcess:
    return remote.run_ssh(remote_ctx["host"], remote_ctx["user"], remote_ctx["secret_path"], script)


def run_case(app_name: str, case: dict, env: dict, base_url: str | None, remote_ctx: dict | None) -> dict:
    target = app_dir(app_name)
    assert target is not None
    case_id = case.get("id") or case["type"]
    case_type = case["type"]

    if case_type == "compose-config":
        if remote_ctx:
            result = _run_remote_script(
                remote_ctx,
                f"docker compose -f {remote_ctx['app_target']}/docker-compose.yml --env-file {remote_ctx['app_target']}/.env config --quiet",
            )
        else:
            result = _run_subprocess([
                "docker", "compose", "-f", str(target / "docker-compose.yml"), "--env-file", str(target / ".env"), "config", "--quiet"
            ])
        return {"id": case_id, "ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}

    if case_type == "container-up":
        if remote_ctx:
            result = _run_remote_script(remote_ctx, "docker ps --format '{{.Names}} {{.Status}}'")
        else:
            result = _run_subprocess(["docker", "ps", "--format", "{{.Names}} {{.Status}}"])
        container_id = env.get("W9_ID", app_name)
        line = _select_container_line(result.stdout, container_id)
        return {"id": case_id, "ok": bool(line and "Up" in line), "stdout": line, "stderr": result.stderr}

    if case_type == "container-healthy":
        container_id = _container_name_prefix(env, app_name)
        if remote_ctx:
            result = _run_remote_script(remote_ctx, f"docker inspect {container_id} --format '{{{{json .State}}}}'")
        else:
            result = _run_subprocess(["docker", "inspect", container_id, "--format", "{{json .State}}"])
        status, health = _inspect_state(result.stdout)
        ok = result.returncode == 0 and status == "running" and health == "healthy"
        return {
            "id": case_id,
            "ok": ok,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": status,
            "health": health,
        }

    if case_type == "web-access":
        if not base_url:
            raise FileNotFoundError("web access requested but no base URL is available")
        path = case.get("path", "/")
        expect = case.get("expect_status", [200])
        return _request_case(case_id, lambda: requests.get(f"{base_url}{path}", timeout=15, allow_redirects=True), expect)

    if case_type == "http-basic":
        if not base_url:
            raise FileNotFoundError("console login requested but no base URL is available")
        path = case.get("path", "/")
        user = env.get(case.get("username_env", "W9_LOGIN_USER"), "")
        password = env.get(case.get("password_env", "W9_LOGIN_PASSWORD"), "")
        expect = case.get("expect_status", 200)
        return _request_case(
            case_id,
            lambda: requests.get(f"{base_url}{path}", timeout=15, allow_redirects=True, auth=(user, password)),
            expect,
        )

    if case_type == "script":
        script = target / "tests" / case["script"]
        if not script.exists():
            raise FileNotFoundError(f"missing test script: {script.relative_to(repo_path())}")
        run_env = {**env, "BASE_URL": base_url or "", "APP_NAME": app_name}
        result = subprocess.run(["bash", str(script)], check=False, capture_output=True, text=True, env=run_env)
        return {"id": case_id, "ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}

    raise ValueError(f"unsupported test type: {case_type}")


def _default_cases(env: dict, compose: dict, base_url: str | None, app_name: str) -> list[dict]:
    cases = [dict(item) for item in DEFAULT_REQUIRED_CASES]
    if _service_has_healthcheck(compose, _main_service_name(app_name, compose, env)):
        cases.append({"id": "container-healthy", "type": "container-healthy"})
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
    wait_timeout: int = 60,
    wait_interval: int = 5,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> dict:
    env = load_env(app_name)
    cases = load_cases(app_name)
    compose = load_compose(app_name)
    resolved_base_url = _base_url(env, base_url, ssh_host)
    remote_ctx = _remote_context(app_name, ssh_host, ssh_user, ssh_secret_path, deploy_root)

    skip_ids = {item["id"] for item in (cases.get("skip") or [])}
    results = []
    required_cases = [case for case in _default_cases(env, compose, resolved_base_url, app_name) if case["id"] not in skip_ids]
    optional_cases = []
    for group in ("optional", "custom"):
        for case in cases.get(group) or []:
            optional_cases.append((group, case))
    total = len(required_cases) + len(optional_cases)
    step = 1

    if remote_ctx:
        preflight = remote.preflight_ssh(remote_ctx["host"], remote_ctx["user"], remote_ctx["secret_path"])
        if preflight.returncode != 0:
            results.append(
                {
                    "id": "remote-connect",
                    "ok": False,
                    "stdout": preflight.stdout,
                    "stderr": preflight.stderr,
                    "error": preflight.stderr or preflight.stdout or "remote SSH connection failed",
                    "group": "required",
                }
            )
            if progress:
                _announce(progress, step, total + 1, "checking remote connectivity")
                if verbose:
                    _emit_case_detail(progress, results[-1])
            return {
                "app": app_name,
                "base_url": resolved_base_url,
                "target": "remote",
                "ok": False,
                "results": results,
            }
        if progress:
            _announce(progress, step, total + 1, "checking remote connectivity")
            if verbose:
                _emit_case_detail(progress, {"id": "remote-connect", "ok": True, "stdout": preflight.stdout, "stderr": preflight.stderr})
        step += 1
        total += 1

    for case in required_cases:
        _announce(progress, step, total, f"running {case['id']}")
        if case["id"] in skip_ids:
            step += 1
            continue

        def attempt() -> dict:
            return run_case(app_name, case, env, resolved_base_url, remote_ctx)

        should_retry = case["type"] in {"container-up", "container-healthy", "web-access", "http-basic"}
        payload = _wait_for(
            wait_timeout,
            wait_interval,
            attempt,
            lambda current: should_retry and not current.get("ok"),
        )
        payload["group"] = "required"
        results.append(payload)
        if progress and verbose:
            _emit_case_detail(progress, payload)
        step += 1
        if not payload.get("ok"):
            break

    if all(item.get("ok") for item in results if item.get("group") == "required"):
        for group, case in optional_cases:
            _announce(progress, step, total, f"running {case.get('id') or case['type']}")
            payload = run_case(app_name, case, env, resolved_base_url, remote_ctx)
            payload["group"] = group
            results.append(payload)
            if progress and verbose:
                _emit_case_detail(progress, payload)
            step += 1

    if progress and verbose:
        progress(f"target={remote_ctx['host'] if remote_ctx else 'local'} base_url={resolved_base_url or ''}".rstrip())

    return {
        "app": app_name,
        "base_url": resolved_base_url,
        "target": "remote" if remote_ctx else "local",
        "ok": all(item.get("ok") for item in results),
        "results": results,
    }
