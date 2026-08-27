from __future__ import annotations

import os
import re
import shlex
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from libs import remote
from libs.metadata import app_dir
from libs.repo import repo_path


ProgressWriter = Callable[[str], None]

W9_VERSION_RE = re.compile(r"^W9_VERSION=.*$", re.MULTILINE)
IMAGE_TAG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


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


def _patched_env_file(app_name: str, version: str) -> Path:
    _validate_tag(version)
    source = app_dir(app_name)
    if not source:
        raise FileNotFoundError(app_name)
    env_path = source / ".env"
    if not env_path.exists():
        raise FileNotFoundError(env_path)
    text = env_path.read_text(encoding="utf-8")
    if not W9_VERSION_RE.search(text):
        raise ValueError(f".env has no W9_VERSION to override: {env_path}")
    text = W9_VERSION_RE.sub(f"W9_VERSION='{version}'", text)
    fd, name = tempfile.mkstemp(prefix=f"libs-deploy-{app_name}-", suffix=".env")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return Path(name)


def _patch_remote_env(
    host: str,
    user: str,
    secret_path: Path,
    app_target: str,
    version: str,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> None:
    _validate_tag(version)
    script = f"sed -i \"s/^W9_VERSION=.*/W9_VERSION='{version}'/\" {app_target}/.env"
    result = _run_remote(host, user, secret_path, script, progress=progress, verbose=verbose)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "remote version patch failed")


def _announce(progress: ProgressWriter | None, index: int, total: int, message: str) -> None:
    if progress:
        progress(f"[{index}/{total}] {message}")


def deploy(
    app_name: str,
    target: str | None = None,
    ssh_host: str | None = None,
    ssh_user: str | None = None,
    ssh_secret_path: str | None = None,
    deploy_root: str | None = None,
    version: str | None = None,
    down: bool = False,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> dict:
    source = app_dir(app_name)
    if not source:
        raise FileNotFoundError(app_name)

    mode = _target_mode(target, ssh_host)
    action = "down -v" if down else "up -d"

    if mode == "local":
        target_path = repo_path("apps", app_name)
        env_file = _patched_env_file(app_name, version) if version else None
        try:
            step = 1
            total = 3 if down else 5

            if not down:
                _announce(progress, step, total, "ensuring shared network")
                _run(["docker", "network", "create", "websoft9"], progress=progress, verbose=verbose)
                step += 1

            _announce(progress, step, total, "validating compose config")
            config = _run(_local_compose_args(target_path, env_file) + ["config", "--quiet"], progress=progress, verbose=verbose)
            if config.returncode != 0:
                raise RuntimeError(config.stderr.strip() or config.stdout.strip() or "compose config failed")

            if not down:
                _announce(progress, step + 1, total, "pulling images")
                pull = _run(_local_compose_args(target_path, env_file) + ["pull"], progress=progress, verbose=verbose)
                if pull.returncode != 0:
                    raise RuntimeError(pull.stderr.strip() or pull.stdout.strip() or "compose pull failed")
                _announce(progress, step + 2, total, "starting application")
                result = _run(_local_compose_args(target_path, env_file) + ["up", "-d"], progress=progress, verbose=verbose)
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

    step = 1
    total = 4 if down else 6

    _announce(progress, step, total, "syncing deploy package")
    _sync_app_dir(app_name, host, user, secret_path, deploy_root_value, progress=progress, verbose=verbose)
    step += 1

    if version:
        _patch_remote_env(host, user, secret_path, app_target, version, progress=progress, verbose=verbose)

    if not down:
        _announce(progress, step, total, "ensuring shared network")
        _run_remote(host, user, secret_path, "docker network create websoft9 || true", progress=progress, verbose=verbose)
        step += 1

    _announce(progress, step, total, "validating compose config")
    config = _run_remote(host, user, secret_path, _remote_compose_script(app_target, "config --quiet"), progress=progress, verbose=verbose)
    if config.returncode != 0:
        raise RuntimeError(config.stderr.strip() or config.stdout.strip() or "remote compose config failed")

    if not down:
        _announce(progress, step + 1, total, "pulling images")
        pull = _run_remote(host, user, secret_path, _remote_compose_script(app_target, "pull"), progress=progress, verbose=verbose)
        if pull.returncode != 0:
            raise RuntimeError(pull.stderr.strip() or pull.stdout.strip() or "remote compose pull failed")
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
        "ps": ps.stdout.strip(),
    }
