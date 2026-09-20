from __future__ import annotations

import base64
import re
import shlex
import subprocess
from collections.abc import Callable
from pathlib import Path

from libs import remote


ProgressWriter = Callable[[str], None]

DEFAULT_TAG = "dev"
DEFAULT_TAG_VAR = "IMAGE_TAG"
TAG_VAR_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
TAG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")

LABEL_WORKING_DIR = "com.docker.compose.project.working_dir"
LABEL_CONFIG_FILES = "com.docker.compose.project.config_files"

COMPOSE_FILENAMES = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")

SshContext = tuple[str, str, Path]


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


def _announce(progress: ProgressWriter | None, index: int, total: int, message: str) -> None:
    if progress:
        progress(f"[{index}/{total}] {message}")


def _validate_tag(tag: str) -> str:
    if not tag or not TAG_RE.fullmatch(tag):
        raise ValueError(f"invalid image tag: {tag!r}")
    return tag


def _validate_tag_var(tag_var: str) -> str:
    if not tag_var or not TAG_VAR_RE.fullmatch(tag_var):
        raise ValueError(f"invalid tag variable name: {tag_var!r}")
    return tag_var


def _target_mode(target: str | None, ssh_host: str | None) -> str:
    if target:
        return target
    if ssh_host:
        return "remote"
    return remote.default_target()


def _resolve_ssh(ssh_host: str | None, ssh_user: str | None, ssh_secret_path: str | None) -> SshContext:
    host = remote.ssh_host(ssh_host)
    if not host:
        raise FileNotFoundError("missing SSH host; pass --ssh-host or set SSH_HOST in .secrets/remote.env")
    user = remote.ssh_user(ssh_user)
    secret_path = remote.resolve_secret_path(ssh_secret_path)
    if not secret_path.exists():
        raise FileNotFoundError(f"SSH secret not found: {secret_path}")
    return host, user, secret_path


def _run_command(
    command: list[str],
    ctx: SshContext | None,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    if ctx is None:
        return _run(command, progress=progress, verbose=verbose)
    host, user, secret_path = ctx
    return _run(remote.ssh_base(host, user, secret_path) + [shlex.join(command)], progress=progress, verbose=verbose)


def _run_remote_script(
    script: str,
    ctx: SshContext,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    host, user, secret_path = ctx
    return _run(remote.ssh_base(host, user, secret_path) + [script], progress=progress, verbose=verbose)


def _inspect_label(
    container: str,
    label: str,
    ctx: SshContext | None,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> str:
    result = _run_command(
        ["docker", "inspect", container, "--format", f'{{{{ index .Config.Labels "{label}" }}}}'],
        ctx,
        progress=progress,
        verbose=verbose,
    )
    if result.returncode != 0:
        raise FileNotFoundError(
            result.stderr.strip() or result.stdout.strip() or f"container not found: {container}"
        )
    return result.stdout.strip()


def _resolve_project(
    container: str,
    compose_dir: str | None,
    ctx: SshContext | None,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> tuple[str, str, str]:
    if compose_dir:
        project_dir = compose_dir.rstrip("/") or "/"
        compose_file = next(
            (f"{project_dir}/{name}" for name in COMPOSE_FILENAMES if _path_exists(f"{project_dir}/{name}", ctx)),
            f"{project_dir}/{COMPOSE_FILENAMES[0]}",
        )
        return project_dir, compose_file, f"{project_dir}/.env"

    working_dir = _inspect_label(container, LABEL_WORKING_DIR, ctx, progress=progress, verbose=verbose)
    config_files = _inspect_label(container, LABEL_CONFIG_FILES, ctx, progress=progress, verbose=verbose)

    compose_file = config_files.split(",")[0].strip() if config_files else ""
    if not compose_file:
        raise FileNotFoundError(
            f"container {container} has no compose config; pass --compose-dir to locate the project"
        )
    project_dir = working_dir or str(Path(compose_file).parent)
    return project_dir, compose_file, f"{project_dir}/.env"


def _path_exists(path: str, ctx: SshContext | None) -> bool:
    if ctx is None:
        return Path(path).exists()
    result = _run_remote_script(f"test -e {shlex.quote(path)}", ctx)
    return result.returncode == 0


def _read_text(path: str, ctx: SshContext | None, *, verbose: bool = False) -> str:
    if ctx is None:
        return Path(path).read_text(encoding="utf-8")
    result = _run_command(["cat", path], ctx, verbose=verbose)
    if result.returncode != 0:
        raise FileNotFoundError(result.stderr.strip() or result.stdout.strip() or f"cannot read {path}")
    return result.stdout


def _write_text(path: str, text: str, ctx: SshContext | None, *, verbose: bool = False) -> None:
    if ctx is None:
        Path(path).write_text(text, encoding="utf-8")
        return
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    result = _run_remote_script(
        f"printf '%s' {encoded} | base64 -d > {shlex.quote(path)}",
        ctx,
        verbose=verbose,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"cannot write {path}")


def _set_env_tag(env_file: str, tag_var: str, tag: str, ctx: SshContext | None, *, verbose: bool = False) -> str | None:
    text = _read_text(env_file, ctx, verbose=verbose)
    pattern = re.compile(rf"^{re.escape(tag_var)}=(.*)$", re.MULTILINE)
    match = pattern.search(text)
    previous = match.group(1).strip().strip('"').strip("'") if match else None

    if match:
        updated = pattern.sub(f"{tag_var}={tag}", text)
    else:
        separator = "" if (not text or text.endswith("\n")) else "\n"
        updated = f"{text}{separator}{tag_var}={tag}\n"

    _write_text(env_file, updated, ctx, verbose=verbose)
    return previous


def upgrade(
    container: str | None = None,
    tag: str = DEFAULT_TAG,
    tag_var: str = DEFAULT_TAG_VAR,
    compose_dir: str | None = None,
    target: str | None = None,
    ssh_host: str | None = None,
    ssh_user: str | None = None,
    ssh_secret_path: str | None = None,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> dict:
    """Point the Websoft9 platform container at an image tag, then pull and recreate it."""
    _validate_tag(tag)
    _validate_tag_var(tag_var)

    mode = _target_mode(target, ssh_host)
    if mode not in ("local", "remote"):
        raise ValueError(f"invalid target: {mode!r}")

    container_name = remote.appstore_container(container)
    ctx = _resolve_ssh(ssh_host, ssh_user, ssh_secret_path) if mode == "remote" else None

    total = 5
    _announce(progress, 1, total, "resolving compose project")
    project_dir, compose_file, env_file = _resolve_project(
        container_name, compose_dir, ctx, progress=progress, verbose=verbose
    )

    _announce(progress, 2, total, f"setting {tag_var}={tag}")
    previous_tag = _set_env_tag(env_file, tag_var, tag, ctx, verbose=verbose)

    compose_base = ["docker", "compose", "-f", compose_file, "--env-file", env_file]

    _announce(progress, 3, total, "pulling image")
    pull = _run_command(compose_base + ["pull"], ctx, progress=progress, verbose=verbose)
    if pull.returncode != 0:
        raise RuntimeError(pull.stderr.strip() or pull.stdout.strip() or "compose pull failed")

    _announce(progress, 4, total, "recreating container")
    up = _run_command(compose_base + ["up", "-d"], ctx, progress=progress, verbose=verbose)
    if up.returncode != 0:
        raise RuntimeError(up.stderr.strip() or up.stdout.strip() or "compose up -d failed")

    _announce(progress, 5, total, "showing container status")
    ps = _run_command(compose_base + ["ps"], ctx, progress=progress, verbose=verbose)

    payload = {
        "container": container_name,
        "target": mode,
        "project_dir": project_dir,
        "compose_file": compose_file,
        "env_file": env_file,
        "tag_var": tag_var,
        "tag": tag,
        "previous_tag": previous_tag,
        "action": "upgrade",
        "ps": ps.stdout.strip(),
    }
    if ctx is not None:
        payload["host"] = ctx[0]
        payload["user"] = ctx[1]
        payload["ssh_secret_path"] = str(ctx[2])
    return payload
