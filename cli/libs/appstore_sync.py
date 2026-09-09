from __future__ import annotations

import shlex
import shutil
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from libs import catalog
from libs import remote
from libs.remote import resolve_secret_path as default_resolve_secret_path
from libs.remote import scp_base, ssh_base
from libs.remote import ssh_host as default_ssh_host
from libs.remote import ssh_user as default_ssh_user
from libs.repo import repo_path

DEFAULT_CONTAINER = "websoft9"
DEFAULT_APP_DEPLOY_DIR = "/websoft9/library/apps"
DEFAULT_CATALOG_DIR = "/websoft9/library/metadata/catalog"
DEFAULT_KEY = ".secrets/ssh/default.pem"

ProgressWriter = Callable[[str], None]


def resolve_secret_path(secret_path: str | None) -> Path:
    return default_resolve_secret_path(secret_path)


def _ssh_shell_prefix(secret_path: Path) -> str:
    opts = " -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15"
    if remote.secret_mode(secret_path) == "key":
        return f"ssh -i {secret_path}{opts}"
    if not shutil.which("sshpass"):
        raise FileNotFoundError("sshpass is required for password-based SSH; provide a key file or install sshpass")
    return f"sshpass -f {secret_path} ssh{opts}"


def _announce(progress: ProgressWriter | None, index: int, total: int, message: str) -> None:
    if progress:
        progress(f"[{index}/{total}] {message}")


def _run(command: list[str], *, progress: ProgressWriter | None = None, verbose: bool = False) -> str:
    if progress and verbose:
        progress(f"$ {shlex.join(command)}")
    result = remote.run_command(command)
    if progress and verbose:
        if result.stdout.strip():
            progress(result.stdout.rstrip())
        if result.stderr.strip():
            progress(result.stderr.rstrip())
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "command failed")
    return result.stdout.strip()


def _sync_app_dir(
    app_name: str,
    host: str,
    user: str,
    secret_path: Path,
    container: str,
    deploy_dir: str,
    backup_dir: str,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> None:
    staging_dir = f"/tmp/websoft9-appstore-staging-{app_name}"
    remote_host = f"{user}@{host}"

    _run(
        ssh_base(host, user, secret_path)
        + [
            (
                f"rm -rf {staging_dir} && mkdir -p {staging_dir} && mkdir -p {backup_dir} && "
                f"if docker exec {container} sh -c 'test -d {deploy_dir}/{app_name}'; then "
                f"docker exec {container} sh -c 'tar czf - -C {deploy_dir} {app_name}' > {backup_dir}/{app_name}.tgz; fi"
            )
        ],
        progress=progress,
        verbose=verbose,
    )

    _run(
        scp_base(host, user, secret_path)
        + ["-r", str(repo_path("apps", app_name)), f"{remote_host}:{staging_dir}/"],
        progress=progress,
        verbose=verbose,
    )

    _run(
        ssh_base(host, user, secret_path)
        + [
            (
                f"docker exec {container} sh -c 'rm -rf {deploy_dir}/{app_name}' && "
                f"docker cp {staging_dir}/{app_name} {container}:{deploy_dir} && "
                f"rm -rf {staging_dir}"
            )
        ],
        progress=progress,
        verbose=verbose,
    )


def _sync_catalog_file(
    app_name: str,
    host: str,
    user: str,
    secret_path: Path,
    container: str,
    catalog_dir: str,
    backup_dir: str,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> str:
    source = repo_path("metadata", "catalog", f"{app_name}.json")
    if not source.exists():
        raise FileNotFoundError(f"repo catalog data not found: metadata/catalog/{app_name}.json")
    catalog.load_catalog(app_name)

    staging_dir = f"/tmp/websoft9-appstore-staging-{app_name}"
    remote_host = f"{user}@{host}"
    backup_name = f"catalog-{app_name}.json.bak"

    _run(
        ssh_base(host, user, secret_path)
        + [
            (
                f"rm -rf {staging_dir} && mkdir -p {staging_dir} && mkdir -p {backup_dir} && "
                f"if docker exec {container} sh -c 'test -f {catalog_dir}/{app_name}.json'; then "
                f"docker cp {container}:{catalog_dir}/{app_name}.json {backup_dir}/{backup_name}; fi"
            )
        ],
        progress=progress,
        verbose=verbose,
    )

    _run(
        scp_base(host, user, secret_path)
        + [str(source), f"{remote_host}:{staging_dir}/"],
        progress=progress,
        verbose=verbose,
    )

    _run(
        ssh_base(host, user, secret_path)
        + [
            (
                f"docker exec {container} sh -c 'mkdir -p {catalog_dir}' && "
                f"docker cp {staging_dir}/{app_name}.json {container}:{catalog_dir}/{app_name}.json && "
                f"rm -rf {staging_dir}"
            )
        ],
        progress=progress,
        verbose=verbose,
    )
    return str(source.relative_to(repo_path()))


def prepare_preview(
    app_name: str,
    host: str | None = None,
    user: str | None = None,
    secret_path: str | None = None,
    container: str = DEFAULT_CONTAINER,
    catalog_dir: str = DEFAULT_CATALOG_DIR,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> dict:
    host = default_ssh_host(host)
    if not host:
        raise FileNotFoundError("missing SSH host; pass --ssh-host or set SSH_HOST in .secrets/remote.env")
    user = default_ssh_user(user)
    container = remote.appstore_container(container)
    key_path = resolve_secret_path(secret_path)
    if not key_path.exists():
        raise FileNotFoundError(f"SSH secret not found: {key_path}")

    target_catalog_dir = catalog_dir.rstrip("/")
    deploy_dir = DEFAULT_APP_DEPLOY_DIR
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backup_dir = f"/tmp/websoft9-appstore-sync-{app_name}-{timestamp}"

    catalog_source = repo_path("metadata", "catalog", f"{app_name}.json")
    has_catalog = catalog_source.exists()
    if has_catalog:
        catalog.load_catalog(app_name)

    total = 2 if has_catalog else 1

    _announce(progress, 1, total, "syncing app directory")
    _sync_app_dir(app_name, host, user, key_path, container, deploy_dir, backup_dir, progress=progress, verbose=verbose)

    catalog_rel = None
    if has_catalog:
        _announce(progress, 2, total, "syncing catalog commercial data")
        catalog_rel = _sync_catalog_file(
            app_name, host, user, key_path, container, target_catalog_dir, backup_dir, progress=progress, verbose=verbose
        )

    rollback = [
        f"{_ssh_shell_prefix(key_path)} {user}@{host} 'if test -f {backup_dir}/{app_name}.tgz; then docker exec {container} sh -c \"rm -rf {deploy_dir}/{app_name}\" && docker exec -i {container} sh -c \"tar xzf - -C {deploy_dir}\" < {backup_dir}/{app_name}.tgz; fi'",
    ]
    if has_catalog:
        rollback.append(
            f"{_ssh_shell_prefix(key_path)} {user}@{host} 'if test -f {backup_dir}/catalog-{app_name}.json.bak; then docker cp {backup_dir}/catalog-{app_name}.json.bak {container}:{target_catalog_dir}/{app_name}.json; fi'"
        )

    return {
        "app": app_name,
        "host": host,
        "user": user,
        "ssh_secret_path": str(key_path),
        "container": container,
        "deploy_dir": deploy_dir,
        "catalog_dir": target_catalog_dir,
        "app_target": f"{deploy_dir}/{app_name}",
        "catalog_source": catalog_rel,
        "catalog_synced": has_catalog,
        "catalog_target": f"{target_catalog_dir}/{app_name}.json",
        "backup_dir": backup_dir,
        "rollback": rollback,
    }
