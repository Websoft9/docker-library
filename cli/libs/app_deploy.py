from __future__ import annotations

import os
import re
import shlex
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

import yaml

from libs import remote
from libs import app_build
from libs.metadata import app_dir
from libs.repo import repo_path


ProgressWriter = Callable[[str], None]

W9_VERSION_RE = re.compile(r"^W9_VERSION=.*$", re.MULTILINE)
IMAGE_TAG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
PORT_REF_RE = re.compile(r"^\$\{?([A-Z0-9_]+)\}?$")
DOCKER_PORT_RE = re.compile(r"(?:0\.0\.0\.0|127\.0\.0\.1|\[::\]|::):(\d+)->")
SS_PORT_RE = re.compile(r":(\d+)\s+\S+\s*$")
FREE_PORT_LOW = 9000
FREE_PORT_HIGH = 9999
PULL_POLICIES = {"always", "missing", "never"}


def _run(command: list[str], *, progress: ProgressWriter | None = None, verbose: bool = False) -> subprocess.CompletedProcess:
    if progress and verbose:
        progress(f"$ {shlex.join(command)}")
    result = remote.run_command(command)
    if progress and verbose:
        if result.stdout.strip():
            progress(result.stdout.rstrip())
        if result.stderr.strip():
            progress(result.stderr.rstrip())
    return result


def _run_remote(host: str, user: str, secret_path: Path, script: str, *, progress: ProgressWriter | None = None, verbose: bool = False) -> subprocess.CompletedProcess:
    return _run(remote.ssh_base(host, user, secret_path) + [script], progress=progress, verbose=verbose)


def _sync_app_dir(
    app_name: str,
    host: str,
    user: str,
    secret_path: Path,
    deploy_root: str,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> None:
    prepare = _run_remote(
        host,
        user,
        secret_path,
        f"mkdir -p {deploy_root} && rm -rf {deploy_root}/{app_name}",
        progress=progress,
        verbose=verbose,
    )
    if prepare.returncode != 0:
        raise RuntimeError(prepare.stderr.strip() or prepare.stdout.strip() or "remote prepare failed")
    copy = _run(
        remote.scp_base(host, user, secret_path) + ["-r", str(repo_path("apps", app_name)), f"{user}@{host}:{deploy_root}/"],
        progress=progress,
        verbose=verbose,
    )
    if copy.returncode != 0:
        raise RuntimeError(copy.stderr.strip() or copy.stdout.strip() or "remote sync failed")


def _local_compose_args(target: Path, env_file: Path | None = None) -> list[str]:
    return [
        "docker",
        "compose",
        "-f",
        str(target / "docker-compose.yml"),
        "--env-file",
        str(env_file if env_file is not None else target / ".env"),
    ]


def _remote_compose_script(target: str, action: str) -> str:
    return f"docker compose -f {target}/docker-compose.yml --env-file {target}/.env {action}"


def _compose_up_action(pull_policy: str) -> str:
    return "up -d --pull never" if pull_policy == "never" else "up -d"


def _compose_services(target: Path) -> dict:
    compose_path = target / "docker-compose.yml"
    if not compose_path.exists():
        return {}
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
    return compose.get("services") or {}


def _pull_services(app_name: str, target: Path) -> list[str]:
    """Services whose images must be pulled (not built locally/remotely)."""
    services = _compose_services(target)
    local_build_refs = set(app_build.build_image_refs(app_name))
    pull = []
    for name, service in services.items():
        if not isinstance(service, dict) or not isinstance(service.get("image"), str):
            continue
        image = service["image"]
        resolved = app_build.resolve_image(app_name, image)
        if image in local_build_refs or resolved in local_build_refs:
            continue
        pull.append(name)
    return pull


def _target_mode(target: str | None, ssh_host: str | None) -> str:
    if target:
        return target
    if ssh_host:
        return "remote"
    return remote.default_target()


def _validate_tag(version: str) -> str:
    if not version or not IMAGE_TAG_RE.fullmatch(version):
        raise ValueError(f"invalid image tag for --version: {version!r}")
    return version


def _env_map(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _compose_published_ports(target: Path, env_map: dict[str, str]) -> list[dict]:
    """Return published host ports declared by the app's compose file."""
    compose_path = target / "docker-compose.yml"
    if not compose_path.exists():
        return []
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
    rows: list[dict] = []
    for service_name, service in (compose.get("services") or {}).items():
        if not isinstance(service, dict):
            continue
        for entry in service.get("ports", []) or []:
            service_name_value = str(service_name)
            if isinstance(entry, dict):
                published = entry.get("published")
                target_port = entry.get("target")
                if published is None or target_port is None:
                    continue
                raw = str(published)
                env_name = _port_env_name(raw)
                value = _resolve_env_value(raw, env_map)
                if value is None:
                    continue
                rows.append({
                    "service": service_name_value,
                    "env": env_name,
                    "published": int(value),
                    "target": target_port,
                })
                continue
            if not isinstance(entry, str):
                continue
            text = entry.strip().strip("'\"")
            parts = text.split(":")
            if len(parts) < 2:
                continue
            host_part = parts[-2]
            target_part = parts[-1].split("/", 1)[0]
            env_name = _port_env_name(host_part)
            value = _resolve_env_value(host_part, env_map)
            if value is None:
                continue
            try:
                rows.append({
                    "service": service_name_value,
                    "env": env_name,
                    "published": int(value),
                    "target": int(target_part),
                })
            except ValueError:
                continue
    return rows


def _port_env_name(value: str) -> str | None:
    match = PORT_REF_RE.match(value.strip())
    return match.group(1) if match else None


def _resolve_env_value(value: str, env_map: dict[str, str]) -> str | None:
    value = value.strip()
    match = PORT_REF_RE.match(value)
    if match:
        resolved = env_map.get(match.group(1))
        return resolved if resolved and resolved.isdigit() else None
    return value if value.isdigit() else None


def _name_is_own(name: str, prefixes: list[str]) -> bool:
    return any(name == prefix or name.startswith(f"{prefix}-") for prefix in prefixes)


def _parse_occupied_ports(text: str, exclude_prefixes: list[str] | None = None) -> set[int]:
    prefixes = exclude_prefixes or []
    ports: set[int] = set()
    excluded: set[int] = set()
    for line in text.splitlines():
        if "|" in line:
            name, raw_ports = line.split("|", 1)
            found = {int(match.group(1)) for match in DOCKER_PORT_RE.finditer(raw_ports)}
            if _name_is_own(name.strip(), prefixes):
                excluded |= found
            else:
                ports |= found
            continue
        match = SS_PORT_RE.search(line)
        if match:
            ports.add(int(match.group(1)))
    return ports - excluded


def _occupied_ports_local(exclude_prefixes: list[str] | None = None) -> set[int]:
    text = ""
    docker_ps = _run(["docker", "ps", "--format", "{{.Names}}|{{.Ports}}"])
    if docker_ps.returncode == 0:
        text += docker_ps.stdout
    ss = _run(["ss", "-ltnH"])
    if ss.returncode == 0:
        text += "\n" + ss.stdout
    return _parse_occupied_ports(text, exclude_prefixes)


def _occupied_ports_remote(host: str, user: str, secret_path: Path, exclude_prefixes: list[str] | None = None) -> set[int]:
    result = _run_remote(host, user, secret_path, "docker ps --format '{{.Names}}|{{.Ports}}'; ss -ltnH 2>/dev/null || true")
    if result.returncode != 0:
        return set()
    return _parse_occupied_ports(result.stdout, exclude_prefixes)


def _pick_free_port(occupied: set[int], preferred: int | None = None) -> int:
    start = preferred if preferred and FREE_PORT_LOW <= preferred <= FREE_PORT_HIGH else FREE_PORT_LOW
    for port in range(start, FREE_PORT_HIGH + 1):
        if port not in occupied:
            return port
    for port in range(FREE_PORT_LOW, start):
        if port not in occupied:
            return port
    raise RuntimeError(f"no free port in {FREE_PORT_LOW}-{FREE_PORT_HIGH}")


def _port_overrides(target: Path, env_map: dict[str, str], occupied: set[int]) -> dict[str, int]:
    overrides: dict[str, int] = {}
    for row in _compose_published_ports(target, env_map):
        env_name = row.get("env")
        published = row["published"]
        if not env_name or env_name in overrides:
            continue
        if published in occupied:
            selected = _pick_free_port(occupied | set(overrides.values()), published)
            overrides[env_name] = selected
    return overrides


def _effective_env_map(env_map: dict[str, str], overrides: dict[str, int]) -> dict[str, str]:
    effective = dict(env_map)
    for key, value in overrides.items():
        effective[key] = str(value)
    return effective


def _base_url(target: Path, env_map: dict[str, str], overrides: dict[str, int], host: str | None) -> str | None:
    effective = _effective_env_map(env_map, overrides)
    ports = _compose_published_ports(target, effective)
    if not ports:
        return None
    for row in ports:
        if row.get("env") == "W9_HTTP_PORT_SET" or row.get("target") == 80:
            scheme = "https" if row.get("env") == "W9_HTTPS_PORT_SET" else "http"
            address = host or "localhost"
            return f"{scheme}://{address}:{row['published']}"
    first = ports[0]
    scheme = "https" if first.get("env") == "W9_HTTPS_PORT_SET" else "http"
    address = host or "localhost"
    return f"{scheme}://{address}:{first['published']}"


def _patched_env_text(text: str, version: str | None, overrides: dict[str, int]) -> str:
    if version:
        _validate_tag(version)
        text = W9_VERSION_RE.sub(f"W9_VERSION='{version}'", text)
    for key, value in overrides.items():
        pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
        if pattern.search(text):
            text = pattern.sub(f"{key}={value}", text)
        else:
            text = text.rstrip("\n") + f"\n{key}={value}\n"
    return text


def _patched_env_file(app_name: str, version: str | None, overrides: dict[str, int] | None = None) -> Path | None:
    overrides = overrides or {}
    if not version and not overrides:
        return None
    source = app_dir(app_name)
    if not source:
        raise FileNotFoundError(app_name)
    env_path = source / ".env"
    if not env_path.exists():
        raise FileNotFoundError(env_path)
    text = _patched_env_text(env_path.read_text(encoding="utf-8"), version, overrides)
    fd, name = tempfile.mkstemp(prefix=f"libs-deploy-{app_name}-", suffix=".env")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return Path(name)


def _patch_remote_env(
    host: str,
    user: str,
    secret_path: Path,
    app_target: str,
    version: str | None,
    overrides: dict[str, int] | None = None,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> None:
    commands: list[str] = []
    if version:
        _validate_tag(version)
        commands.append(f"sed -i \"s/^W9_VERSION=.*/W9_VERSION='{version}'/\" {app_target}/.env")
    for key, value in (overrides or {}).items():
        commands.append(f"sed -i \"s/^{re.escape(key)}=.*/{key}={value}/\" {app_target}/.env")
    if not commands:
        return
    result = _run_remote(host, user, secret_path, " && ".join(commands), progress=progress, verbose=verbose)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "remote env patch failed")


def _announce(progress: ProgressWriter | None, index: int, total: int, message: str) -> None:
    if progress:
        progress(f"[{index}/{total}] {message}")


def _build_via_app_build(
    app_name: str,
    mode: str,
    *,
    ssh_host: str | None = None,
    ssh_user: str | None = None,
    ssh_secret_path: str | None = None,
    deploy_root: str | None = None,
    compose_env_file: str | None = None,
    progress: ProgressWriter | None = None,
) -> None:
    """Delegate image build to app_build so deploy and build share one implementation."""
    app_build.build_app(
        app_name,
        push=False,
        target=mode,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_secret_path=ssh_secret_path,
        deploy_root=deploy_root,
        compose_env_file=compose_env_file,
        skip_sync=(mode == "remote"),
        progress=progress,
    )


def deploy(
    app_name: str,
    target: str | None = None,
    ssh_host: str | None = None,
    ssh_user: str | None = None,
    ssh_secret_path: str | None = None,
    deploy_root: str | None = None,
    version: str | None = None,
    down: bool = False,
    auto_port: bool = True,
    pull_policy: str = "always",
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> dict:
    source = app_dir(app_name)
    if not source:
        raise FileNotFoundError(app_name)
    if pull_policy not in PULL_POLICIES:
        raise ValueError(f"invalid pull policy: {pull_policy}; expected one of {sorted(PULL_POLICIES)}")

    mode = _target_mode(target, ssh_host)
    action = "down -v" if down else "up -d"
    needs_build = app_build.can_build(app_name)
    pull_services = _pull_services(app_name, source)
    env_map = _env_map(source / ".env")
    published_ports = _compose_published_ports(source, env_map)
    own_prefixes = [env_map.get("W9_ID", app_name)]

    if mode == "local":
        target_path = repo_path("apps", app_name)
        overrides: dict[str, int] = {}
        if auto_port and not down and published_ports:
            overrides = _port_overrides(target_path, env_map, _occupied_ports_local(own_prefixes))
        env_file = _patched_env_file(app_name, version, overrides)
        base_url = _base_url(target_path, env_map, overrides, None)
        try:
            step = 1
            total = 3 if down else (6 if needs_build else 5)

            if not down:
                _announce(progress, step, total, "ensuring shared network")
                _run(["docker", "network", "create", "websoft9"], progress=progress, verbose=verbose)
                step += 1

            _announce(progress, step, total, "validating compose config")
            config = _run(_local_compose_args(target_path, env_file) + ["config", "--quiet"], progress=progress, verbose=verbose)
            if config.returncode != 0:
                raise RuntimeError(config.stderr.strip() or config.stdout.strip() or "compose config failed")

            if not down:
                _announce(progress, step + 1, total, "pulling images" if pull_policy != "never" else "using existing images")
                if pull_services and pull_policy != "never":
                    pull = _run(_local_compose_args(target_path, env_file) + ["pull", "--policy", pull_policy, *pull_services], progress=progress, verbose=verbose)
                    if pull.returncode != 0:
                        raise RuntimeError(pull.stderr.strip() or pull.stdout.strip() or "compose pull failed")
                if needs_build:
                    _announce(progress, step + 2, total, "building local images")
                    _build_via_app_build(
                        app_name,
                        "local",
                        compose_env_file=str(env_file) if env_file else None,
                        progress=progress,
                    )
                    _announce(progress, step + 3, total, "starting application")
                    result = _run(_local_compose_args(target_path, env_file) + _compose_up_action(pull_policy).split(), progress=progress, verbose=verbose)
                    ps_step = step + 4
                else:
                    _announce(progress, step + 2, total, "starting application")
                    result = _run(_local_compose_args(target_path, env_file) + _compose_up_action(pull_policy).split(), progress=progress, verbose=verbose)
                    ps_step = step + 3
            else:
                _announce(progress, step + 1, total, "stopping application")
                result = _run(_local_compose_args(target_path, env_file) + ["down", "-v"], progress=progress, verbose=verbose)
                ps_step = step + 2
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"compose {action} failed")

            _announce(progress, ps_step, total, "showing container status")
            ps = _run(_local_compose_args(target_path, env_file) + ["ps"], progress=progress, verbose=verbose)
            return {
                "app": app_name,
                "target": "local",
                "version": version,
                "deploy_root": str(repo_path("apps")),
                "app_target": str(target_path),
                "action": action,
                "pull_policy": pull_policy,
                "port_overrides": {key: str(value) for key, value in overrides.items()},
                "base_url": base_url,
                "ps": ps.stdout.strip(),
            }
        finally:
            if env_file is not None:
                env_file.unlink(missing_ok=True)

    host = remote.ssh_host(ssh_host)
    if not host:
        raise FileNotFoundError("missing SSH host; pass --ssh-host or set SSH_HOST in .secrets/remote.env")
    user = remote.ssh_user(ssh_user)
    secret_path = remote.resolve_secret_path(ssh_secret_path)
    if not secret_path.exists():
        raise FileNotFoundError(f"SSH secret not found: {secret_path}")
    deploy_root_value = remote.deploy_root(deploy_root)
    app_target = f"{deploy_root_value}/{app_name}"

    overrides: dict[str, int] = {}
    if auto_port and not down and published_ports:
        overrides = _port_overrides(source, env_map, _occupied_ports_remote(host, user, secret_path, own_prefixes))
    base_url = _base_url(source, env_map, overrides, host)

    step = 1
    total = 4 if down else (7 if needs_build else 6)

    _announce(progress, step, total, "syncing deploy package")
    _sync_app_dir(app_name, host, user, secret_path, deploy_root_value, progress=progress, verbose=verbose)
    step += 1

    if version or overrides:
        _patch_remote_env(host, user, secret_path, app_target, version, overrides, progress=progress, verbose=verbose)

    if not down:
        _announce(progress, step, total, "ensuring shared network")
        _run_remote(host, user, secret_path, "docker network create websoft9 || true", progress=progress, verbose=verbose)
        step += 1

    _announce(progress, step, total, "validating compose config")
    config = _run_remote(host, user, secret_path, _remote_compose_script(app_target, "config --quiet"), progress=progress, verbose=verbose)
    if config.returncode != 0:
        raise RuntimeError(config.stderr.strip() or config.stdout.strip() or "remote compose config failed")

    if not down:
        _announce(progress, step + 1, total, "pulling images" if pull_policy != "never" else "using existing images")
        if pull_services and pull_policy != "never":
            pull = _run_remote(host, user, secret_path, _remote_compose_script(app_target, f"pull --policy {pull_policy} {' '.join(pull_services)}"), progress=progress, verbose=verbose)
            if pull.returncode != 0:
                raise RuntimeError(pull.stderr.strip() or pull.stdout.strip() or "remote compose pull failed")
        if needs_build:
            _announce(progress, step + 2, total, "building application images")
            _build_via_app_build(
                app_name,
                "remote",
                ssh_host=host,
                ssh_user=user,
                ssh_secret_path=str(secret_path),
                deploy_root=deploy_root_value,
                progress=progress,
            )
            _announce(progress, step + 3, total, "starting application")
            result = _run_remote(host, user, secret_path, _remote_compose_script(app_target, _compose_up_action(pull_policy)), progress=progress, verbose=verbose)
            ps_step = step + 4
        else:
            _announce(progress, step + 2, total, "starting application")
            result = _run_remote(host, user, secret_path, _remote_compose_script(app_target, "up -d"), progress=progress, verbose=verbose)
            ps_step = step + 3
    else:
        _announce(progress, step + 1, total, "stopping application")
        result = _run_remote(host, user, secret_path, _remote_compose_script(app_target, "down -v"), progress=progress, verbose=verbose)
        ps_step = step + 2
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"remote compose {action} failed")

    _announce(progress, ps_step, total, "showing container status")
    ps = _run_remote(host, user, secret_path, _remote_compose_script(app_target, "ps"), progress=progress, verbose=verbose)
    return {
        "app": app_name,
        "target": "remote",
        "host": host,
        "user": user,
        "ssh_secret_path": str(secret_path),
        "deploy_root": deploy_root_value,
        "app_target": app_target,
        "version": version,
        "action": action,
        "pull_policy": pull_policy,
        "port_overrides": {key: str(value) for key, value in overrides.items()},
        "base_url": base_url,
        "ps": ps.stdout.strip(),
    }
