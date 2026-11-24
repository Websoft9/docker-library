from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from libs import remote
from libs import app_build
from libs.access import UNMANAGED_PORTS_KEY, URL_SCHEMES, VARIABLE_RE
from libs.metadata import app_dir
from libs.repo import repo_path


ProgressWriter = Callable[[str], None]

W9_VERSION_RE = re.compile(r"^W9_VERSION=.*$", re.MULTILINE)
IMAGE_TAG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
PORT_REF_RE = re.compile(r"^\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?$")
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


def _local_compose_args(
    target: Path,
    env_file: Path | None = None,
    compose_file: Path | None = None,
) -> list[str]:
    args = ["docker", "compose"]
    if compose_file is not None:
        args.extend(["--project-directory", str(target), "-f", str(compose_file)])
    else:
        args.extend(["-f", str(target / "docker-compose.yml")])
    args.extend(["--env-file", str(env_file if env_file is not None else target / ".env")])
    return args


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


def _compose_port_bindings(target: Path, env_map: dict[str, str]) -> list[dict]:
    """Return resolved published port bindings including transport protocol."""
    compose_path = target / "docker-compose.yml"
    if not compose_path.exists():
        return []
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
    rows: list[dict] = []
    for service_name, service in (compose.get("services") or {}).items():
        if not isinstance(service, dict) or service.get("profiles"):
            continue
        unmanaged = service.get(UNMANAGED_PORTS_KEY) or {}
        for entry in service.get("ports", []) or []:
            service_name_value = str(service_name)
            if isinstance(entry, dict):
                published = entry.get("published")
                target_raw = entry.get("target")
                if published is None or target_raw is None:
                    continue
                raw = str(published)
                env_name = _port_env_name(raw)
                value = _resolve_env_value(raw, env_map)
                target_val = _resolve_env_value(str(target_raw), env_map)
                if value is None or target_val is None:
                    continue
                protocol = str(entry.get("protocol") or "tcp").lower()
                rows.append({
                    "service": service_name_value,
                    "env": env_name,
                    "published": int(value),
                    "target": int(target_val),
                    "protocol": protocol,
                    "unmanaged": f"{target_val}/{protocol}" in unmanaged,
                })
                continue
            if not isinstance(entry, str):
                continue
            text = entry.strip().strip("'\"")
            parts = text.split(":")
            if len(parts) < 2:
                continue
            host_part = parts[-2]
            tail = parts[-1]
            target_part, protocol = (tail.split("/", 1) + ["tcp"])[:2]
            env_name = _port_env_name(host_part)
            value = _resolve_env_value(host_part, env_map)
            target_val = _resolve_env_value(target_part, env_map)
            if value is None or target_val is None:
                continue
            rows.append({
                "service": service_name_value,
                "env": env_name,
                "published": int(value),
                "target": int(target_val),
                "protocol": protocol.lower(),
                "unmanaged": f"{target_val}/{protocol.lower()}" in unmanaged,
            })
    return rows


def _compose_published_ports(target: Path, env_map: dict[str, str]) -> list[dict]:
    """Return published host ports declared by the app's compose file."""
    return [
        {
            "service": row["service"],
            "env": row["env"],
            "published": row["published"],
            "target": row["target"],
        }
        for row in _compose_port_bindings(target, env_map)
    ]


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


def _access_groups(target: Path, env_map: dict[str, str]) -> list[dict] | None:
    variables_path = target / "variables.json"
    if not variables_path.exists():
        return None
    try:
        variables = json.loads(variables_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(variables, dict):
        return []
    if not isinstance(variables.get("access"), list):
        return None
    groups = [group for group in variables["access"] if isinstance(group, dict)]
    resolved_groups: list[dict] = []
    for group in groups:
        port = group.get("port")
        if isinstance(port, str):
            ref = VARIABLE_RE.fullmatch(port)
            raw = env_map.get(ref.group(1)) if ref else None
            port = int(raw) if raw and raw.isdigit() else None
        if isinstance(port, int) and not isinstance(port, bool):
            resolved_groups.append({**group, "resolved_port": port, "protocol": (group.get("protocol") or "tcp").lower()})
    return resolved_groups


def _rebound_address(value: str, old: int, new: int, *, url: bool) -> str | None:
    if not value:
        return None
    if not url and "," in value:
        return None
    try:
        address = urlsplit(value if url else f"//{value}")
        port = address.port
    except ValueError:
        return None
    if not address.hostname or address.username is not None or not address.netloc:
        return None
    default_port = {"http": 80, "https": 443, "ws": 80, "wss": 443}.get(address.scheme)
    if (port or default_port) != old:
        return None
    host = address.netloc.rsplit(":", 1)[0] if port is not None else address.netloc
    return address._replace(netloc=f"{host}:{new}").geturl() if url else f"{host}:{new}"


def _plan_port_overrides(
    target: Path,
    env_map: dict[str, str],
    occupied: set[int],
) -> tuple[dict[str, int | str], dict[tuple[str, int, str], int], dict[str, str]]:
    env_overrides: dict[str, int | str] = {}
    literal_overrides: dict[tuple[str, int, str], int] = {}
    summary: dict[str, str] = {}
    bindings = _compose_port_bindings(target, env_map)
    reserved = occupied | {row["published"] for row in bindings}
    groups_by_target = {
        (group.get("service"), group["resolved_port"], group["protocol"]): group
        for group in _access_groups(target, env_map) or []
    }
    for row in bindings:
        env_name = row.get("env")
        published = row["published"]
        if published not in occupied or row["unmanaged"]:
            continue
        key = (row["service"], row["target"], row["protocol"])
        if env_name:
            existing = env_overrides.get(env_name)
            selected = existing if isinstance(existing, int) else _pick_free_port(reserved, published)
            env_overrides[env_name] = selected
            summary[env_name] = str(selected)
        else:
            if key in literal_overrides:
                continue
            selected = _pick_free_port(reserved, published)
            literal_overrides[key] = selected
            label = f"{row['service']}:{row['target']}" if row["protocol"] == "tcp" else f"{row['service']}:{row['target']}/{row['protocol']}"
            summary[label] = str(selected)
        reserved.add(selected)
        group = groups_by_target.get(key, {})
        for mapped_var in group.get("mappedPort", []):
            env_overrides[mapped_var] = selected
            summary[mapped_var] = str(selected)
        for field in ("rootUrl", "host"):
            for name in group.get(field, []):
                value = _rebound_address(env_map.get(name, ""), published, selected, url=field == "rootUrl")
                if value is not None:
                    env_overrides[name] = value
    return env_overrides, literal_overrides, summary


def _port_overrides(target: Path, env_map: dict[str, str], occupied: set[int]) -> dict[str, int | str]:
    env_overrides, _, _ = _plan_port_overrides(target, env_map, occupied)
    return env_overrides


def _effective_env_map(env_map: dict[str, str], overrides: dict[str, int | str]) -> dict[str, str]:
    effective = dict(env_map)
    for key, value in overrides.items():
        effective[key] = str(value)
    return effective


def _base_url(
    target: Path,
    env_map: dict[str, str],
    overrides: dict[str, int | str],
    host: str | None,
    literal_overrides: dict[tuple[str, int, str], int] | None = None,
) -> str | None:
    effective = _effective_env_map(env_map, overrides)
    bindings = _compose_port_bindings(target, effective)
    if not bindings:
        return None
    literal_map = literal_overrides or {}
    effective_bindings = [
        {
            **row,
            "published": literal_map.get((row["service"], row["target"], row["protocol"]), row["published"]),
        }
        for row in bindings
    ]
    address = host or "localhost"
    if ":" in address and not address.startswith("["):
        address = f"[{address}]"
    groups = _access_groups(target, effective)
    for group in groups or []:
        url_schemes = [
            endpoint.get("scheme")
            for endpoint in (group.get("endpoints") or [])
            if isinstance(endpoint, dict) and endpoint.get("scheme") in URL_SCHEMES
        ]
        if not url_schemes:
            continue
        for row in effective_bindings:
            if (
                row["service"] == group.get("service")
                and row["target"] == group["resolved_port"]
                and row["protocol"] == group["protocol"]
            ):
                scheme = "https" if url_schemes[0] in {"https", "wss"} else "http"
                return f"{scheme}://{address}:{row['published']}"
    if groups is not None:
        return None
    for row in effective_bindings:
        if row.get("env") in {"W9_HTTP_PORT_SET", "W9_HTTPS_PORT_SET"} or row.get("target") == 80:
            scheme = "https" if row.get("env") == "W9_HTTPS_PORT_SET" else "http"
            return f"{scheme}://{address}:{row['published']}"
    first = effective_bindings[0]
    scheme = "https" if first.get("env") == "W9_HTTPS_PORT_SET" else "http"
    return f"{scheme}://{address}:{first['published']}"


def _patched_compose_text(
    compose_text: str,
    literal_overrides: dict[tuple[str, int, str], int],
    env_map: dict[str, str],
    env_file: Path | None = None,
) -> str:
    compose = yaml.safe_load(compose_text) or {}
    for service_name, service in (compose.get("services") or {}).items():
        if not isinstance(service, dict):
            continue
        if env_file is not None and "env_file" in service:
            raw_env_file = service["env_file"]
            if raw_env_file == ".env":
                service["env_file"] = str(env_file)
            elif isinstance(raw_env_file, list):
                service["env_file"] = [str(env_file) if item == ".env" else item for item in raw_env_file]
        ports = service.get("ports")
        if not isinstance(ports, list):
            continue
        updated_ports = []
        for entry in ports:
            if isinstance(entry, dict):
                target_val = _resolve_env_value(str(entry.get("target", "")), env_map)
                protocol = str(entry.get("protocol") or "tcp").lower()
                key = (str(service_name), int(target_val), protocol) if target_val is not None else None
                if key in literal_overrides and not _port_env_name(str(entry.get("published", ""))):
                    new_val = literal_overrides[key]
                    updated_ports.append({
                        **entry,
                        "published": int(new_val) if isinstance(entry.get("published"), int) else str(new_val),
                    })
                else:
                    updated_ports.append(entry)
                continue
            if not isinstance(entry, str):
                updated_ports.append(entry)
                continue
            text = entry.strip().strip("'\"")
            parts = text.split(":")
            if len(parts) < 2:
                updated_ports.append(entry)
                continue
            host_part = parts[-2]
            tail = parts[-1]
            target_part, protocol = (tail.split("/", 1) + ["tcp"])[:2]
            target_val = _resolve_env_value(target_part, env_map)
            key = (str(service_name), int(target_val), protocol.lower()) if target_val is not None else None
            if key in literal_overrides and not _port_env_name(host_part):
                prefix = ":".join(parts[:-2])
                rebuilt = f"{literal_overrides[key]}:{tail}"
                updated_ports.append(f"{prefix}:{rebuilt}" if prefix else rebuilt)
            else:
                updated_ports.append(entry)
        service["ports"] = updated_ports
    return yaml.safe_dump(compose, sort_keys=False)


def _patched_compose_file(
    app_name: str,
    literal_overrides: dict[tuple[str, int, str], int] | None,
    env_map: dict[str, str],
    env_file: Path | None = None,
) -> Path | None:
    if not literal_overrides and env_file is None:
        return None
    source = app_dir(app_name)
    if not source:
        raise FileNotFoundError(app_name)
    compose_path = source / "docker-compose.yml"
    text = _patched_compose_text(compose_path.read_text(encoding="utf-8"), literal_overrides or {}, env_map, env_file)
    fd, name = tempfile.mkstemp(prefix=f"libs-deploy-{app_name}-", suffix=".yml")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return Path(name)


def _patch_remote_compose(
    app_name: str,
    host: str,
    user: str,
    secret_path: Path,
    app_target: str,
    literal_overrides: dict[tuple[str, int, str], int] | None,
    env_map: dict[str, str],
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> None:
    temp_compose = _patched_compose_file(app_name, literal_overrides, env_map)
    if temp_compose is None:
        return
    try:
        copy = _run(
            remote.scp_base(host, user, secret_path) + [str(temp_compose), f"{user}@{host}:{app_target}/docker-compose.yml"],
            progress=progress,
            verbose=verbose,
        )
        if copy.returncode != 0:
            raise RuntimeError(copy.stderr.strip() or copy.stdout.strip() or "remote compose patch failed")
    finally:
        temp_compose.unlink(missing_ok=True)


def _patched_env_text(text: str, version: str | None, overrides: dict[str, int | str]) -> str:
    if version:
        _validate_tag(version)
        text = W9_VERSION_RE.sub(f"W9_VERSION='{version}'", text)
    for key, value in overrides.items():
        pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
        if pattern.search(text):
            text = pattern.sub(lambda _: f"{key}={value}", text)
        else:
            text = text.rstrip("\n") + f"\n{key}={value}\n"
    return text


def _patched_env_file(app_name: str, version: str | None, overrides: dict[str, int | str] | None = None) -> Path | None:
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
    overrides: dict[str, int | str] | None = None,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> None:
    commands: list[str] = []
    if version:
        _validate_tag(version)
        commands.append(f"sed -i \"s/^W9_VERSION=.*/W9_VERSION='{version}'/\" {app_target}/.env")
    for key, value in (overrides or {}).items():
        replacement = re.sub(r"[\\&|]", lambda m: "\\" + m[0], str(value))
        expression = shlex.quote(f"s|^{re.escape(key)}=.*|{key}={replacement}|")
        commands.append(f"sed -i {expression} {shlex.quote(f'{app_target}/.env')}")
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
        ssh_user=user if (user := ssh_user) else None,
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
        overrides: dict[str, int | str] = {}
        literal_overrides: dict[tuple[str, int, str], int] = {}
        override_summary: dict[str, str] = {}
        if auto_port and not down and published_ports:
            overrides, literal_overrides, override_summary = _plan_port_overrides(
                target_path, env_map, _occupied_ports_local(own_prefixes)
            )
        env_file = _patched_env_file(app_name, version, overrides)
        compose_file = _patched_compose_file(app_name, literal_overrides, _effective_env_map(env_map, overrides), env_file)
        base_url = _base_url(target_path, env_map, overrides, None, literal_overrides)
        try:
            step = 1
            total = 3 if down else (6 if needs_build else 5)

            if not down:
                _announce(progress, step, total, "ensuring shared network")
                _run(["docker", "network", "create", "websoft9"], progress=progress, verbose=verbose)
                step += 1

            _announce(progress, step, total, "validating compose config")
            config = _run(_local_compose_args(target_path, env_file, compose_file) + ["config", "--quiet"], progress=progress, verbose=verbose)
            if config.returncode != 0:
                raise RuntimeError(config.stderr.strip() or config.stdout.strip() or "compose config failed")

            if not down:
                _announce(progress, step + 1, total, "pulling images" if pull_policy != "never" else "using existing images")
                if pull_services and pull_policy != "never":
                    pull = _run(_local_compose_args(target_path, env_file, compose_file) + ["pull", "--policy", pull_policy, *pull_services], progress=progress, verbose=verbose)
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
                    result = _run(_local_compose_args(target_path, env_file, compose_file) + _compose_up_action(pull_policy).split(), progress=progress, verbose=verbose)
                    ps_step = step + 4
                else:
                    _announce(progress, step + 2, total, "starting application")
                    result = _run(_local_compose_args(target_path, env_file, compose_file) + _compose_up_action(pull_policy).split(), progress=progress, verbose=verbose)
                    ps_step = step + 3
            else:
                _announce(progress, step + 1, total, "stopping application")
                result = _run(_local_compose_args(target_path, env_file, compose_file) + ["down", "-v"], progress=progress, verbose=verbose)
                ps_step = step + 2
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"compose {action} failed")

            _announce(progress, ps_step, total, "showing container status")
            ps = _run(_local_compose_args(target_path, env_file, compose_file) + ["ps"], progress=progress, verbose=verbose)
            return {
                "app": app_name,
                "target": "local",
                "version": version,
                "deploy_root": str(repo_path("apps")),
                "app_target": str(target_path),
                "action": action,
                "pull_policy": pull_policy,
                "port_overrides": override_summary,
                "base_url": base_url,
                "ps": ps.stdout.strip(),
            }
        finally:
            if env_file is not None:
                env_file.unlink(missing_ok=True)
            if compose_file is not None:
                compose_file.unlink(missing_ok=True)

    host = remote.ssh_host(ssh_host)
    if not host:
        raise FileNotFoundError("missing SSH host; pass --ssh-host or set SSH_HOST in .secrets/remote.env")
    user = remote.ssh_user(ssh_user)
    secret_path = remote.resolve_secret_path(ssh_secret_path)
    if not secret_path.exists():
        raise FileNotFoundError(f"SSH secret not found: {secret_path}")
    deploy_root_value = remote.deploy_root(deploy_root)
    app_target = f"{deploy_root_value}/{app_name}"

    overrides: dict[str, int | str] = {}
    literal_overrides: dict[tuple[str, int, str], int] = {}
    override_summary: dict[str, str] = {}
    if auto_port and not down and published_ports:
        overrides, literal_overrides, override_summary = _plan_port_overrides(
            source, env_map, _occupied_ports_remote(host, user, secret_path, own_prefixes)
        )
    base_url = _base_url(source, env_map, overrides, host, literal_overrides)

    step = 1
    total = 4 if down else (7 if needs_build else 6)

    _announce(progress, step, total, "syncing deploy package")
    _sync_app_dir(app_name, host, user, secret_path, deploy_root_value, progress=progress, verbose=verbose)
    step += 1

    if version or overrides:
        _patch_remote_env(host, user, secret_path, app_target, version, overrides, progress=progress, verbose=verbose)
    if literal_overrides:
        _patch_remote_compose(
            app_name,
            host,
            user,
            secret_path,
            app_target,
            literal_overrides,
            _effective_env_map(env_map, overrides),
            progress=progress,
            verbose=verbose,
        )

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
        "port_overrides": override_summary,
        "base_url": base_url,
        "ps": ps.stdout.strip(),
    }
