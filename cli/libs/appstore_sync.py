from __future__ import annotations

import shlex
import hashlib
import json
import shutil
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

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
DEFAULT_METADATA_DIR = "/websoft9/library/metadata"
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


def _stage_app_dir(app_name: str, version: str | None) -> tuple[Path, Path | None]:
    """Return the app directory to upload and an optional temp root to clean up.

    A version override is applied only to a temporary copy so the repository
    .env and the app's supported-version metadata stay untouched.
    """
    source = repo_path("apps", app_name)
    if not version:
        return source, None
    if not source.is_dir():
        raise FileNotFoundError(f"repo app directory not found: apps/{app_name}")
    temp_root = Path(tempfile.mkdtemp(prefix=f"libs-appstore-sync-{app_name}-"))
    staged = temp_root / app_name
    shutil.copytree(source, staged)
    env_path = staged / ".env"
    if not env_path.is_file():
        shutil.rmtree(temp_root, ignore_errors=True)
        raise FileNotFoundError(f"repo app .env not found: apps/{app_name}/.env")
    lines = env_path.read_text(encoding="utf-8").splitlines()
    replaced = False
    updated = []
    for line in lines:
        if line.startswith("W9_VERSION="):
            updated.append(f"W9_VERSION={version}")
            replaced = True
        else:
            updated.append(line)
    if not replaced:
        updated.append(f"W9_VERSION={version}")
    env_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
    return staged, temp_root


def _sync_app_dir(
    app_name: str,
    host: str,
    user: str,
    secret_path: Path,
    container: str,
    deploy_dir: str,
    backup_dir: str,
    *,
    version: str | None = None,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> None:
    staging_dir = f"/tmp/websoft9-appstore-staging-{app_name}"
    remote_host = f"{user}@{host}"
    staged_dir, cleanup = _stage_app_dir(app_name, version)

    try:
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
            + ["-r", str(staged_dir), f"{remote_host}:{staging_dir}/"],
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
        # A successful copy is insufficient: bootstrap can replace the library
        # concurrently. Read back the exact staged bytes before reporting ready.
        checksums = "\n".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  ./{path.relative_to(staged_dir).as_posix()}"
            for path in sorted(staged_dir.rglob("*")) if path.is_file()
        ) + "\n"
        verify = (
            f"cd {shlex.quote(f'{deploy_dir}/{app_name}')} && "
            f"printf %s {shlex.quote(checksums)} | sha256sum -c -"
        )
        _run(
            ssh_base(host, user, secret_path)
            + [shlex.join(["docker", "exec", container, "sh", "-c", verify])],
            progress=progress,
            verbose=verbose,
        )
    finally:
        if cleanup is not None:
            shutil.rmtree(cleanup, ignore_errors=True)


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


def _sync_database_types(
    app_name: str,
    host: str,
    user: str,
    secret_path: Path,
    container: str,
    backup_dir: str,
    *,
    progress: ProgressWriter | None = None,
    verbose: bool = False,
) -> str:
    source = repo_path("metadata", "database-types.json")
    try:
        definitions = json.loads(source.read_text(encoding="utf-8"))
        schema = json.loads(repo_path("metadata", "variables.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/databaseTypes"}).validate(definitions)
    except (ValueError, KeyError, jsonschema.ValidationError) as error:
        raise ValueError("Invalid shared database dictionary; repair it before syncing.") from error
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    staging = f"/tmp/websoft9-appstore-staging-{app_name}-database-types"
    target = f"{DEFAULT_METADATA_DIR}/database-types.json"
    temporary = f"{DEFAULT_METADATA_DIR}/.database-types-{digest}.tmp"
    backup = f"{backup_dir}/database-types.json.bak"
    _run(
        ssh_base(host, user, secret_path) + [
            f"mkdir -p {shlex.quote(staging)} {shlex.quote(backup_dir)} && "
            f"if {shlex.join(['docker', 'exec', container, 'test', '-f', target])}; then "
            f"{shlex.join(['docker', 'cp', f'{container}:{target}', backup])}; "
            f"else touch {shlex.quote(backup + '.missing')}; fi"
        ], progress=progress, verbose=verbose,
    )
    _run(
        scp_base(host, user, secret_path) + [str(source), f"{user}@{host}:{staging}/"],
        progress=progress, verbose=verbose,
    )
    verify_and_replace = (
        f"printf %s {shlex.quote(f'{digest}  {temporary}' + chr(10))} | sha256sum -c - && "
        f"mv {shlex.quote(temporary)} {shlex.quote(target)}"
    )
    command = " && ".join([
        shlex.join(["docker", "exec", container, "mkdir", "-p", DEFAULT_METADATA_DIR]),
        shlex.join(["docker", "cp", f"{staging}/database-types.json", f"{container}:{temporary}"]),
        shlex.join(["docker", "exec", container, "sh", "-c", verify_and_replace]),
        f"rm -rf {shlex.quote(staging)}",
    ])
    _run(ssh_base(host, user, secret_path) + [command], progress=progress, verbose=verbose)
    return digest


def prepare_preview(
    app_name: str,
    host: str | None = None,
    user: str | None = None,
    secret_path: str | None = None,
    container: str = DEFAULT_CONTAINER,
    catalog_dir: str = DEFAULT_CATALOG_DIR,
    version: str | None = None,
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

    from libs.validate import _database_metadata_result

    metadata_check = _database_metadata_result(repo_path("apps", app_name))
    if not metadata_check["ok"]:
        raise ValueError("Invalid database declaration; run libs app-check before appstore-sync.")
    if not repo_path("metadata", "database-types.json").is_file():
        raise FileNotFoundError("missing metadata/database-types.json")
    catalog_source = repo_path("metadata", "catalog", f"{app_name}.json")
    has_catalog = catalog_source.exists()
    if has_catalog:
        catalog.load_catalog(app_name)

    total = 3 if has_catalog else 2

    _announce(progress, 1, total, "syncing shared database dictionary")
    database_types_sha256 = _sync_database_types(
        app_name, host, user, key_path, container, backup_dir, progress=progress, verbose=verbose,
    )

    _announce(progress, 2, total, "syncing app directory")
    _sync_app_dir(
        app_name,
        host,
        user,
        key_path,
        container,
        deploy_dir,
        backup_dir,
        version=version,
        progress=progress,
        verbose=verbose,
    )

    catalog_rel = None
    if has_catalog:
        _announce(progress, 3, total, "syncing catalog commercial data")
        catalog_rel = _sync_catalog_file(
            app_name, host, user, key_path, container, target_catalog_dir, backup_dir, progress=progress, verbose=verbose
        )

    rollback = [
        f"{_ssh_shell_prefix(key_path)} {user}@{host} 'if test -f {backup_dir}/{app_name}.tgz; then docker exec {container} sh -c \"rm -rf {deploy_dir}/{app_name}\" && docker exec -i {container} sh -c \"tar xzf - -C {deploy_dir}\" < {backup_dir}/{app_name}.tgz; fi'",
        f"{_ssh_shell_prefix(key_path)} {user}@{host} 'if test -f {backup_dir}/database-types.json.bak; then docker cp {backup_dir}/database-types.json.bak {container}:{DEFAULT_METADATA_DIR}/database-types.json; elif test -f {backup_dir}/database-types.json.bak.missing; then docker exec {container} rm -f {DEFAULT_METADATA_DIR}/database-types.json; fi'",
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
        "database_types_synced": True,
        "database_types_sha256": database_types_sha256,
        "database_types_target": f"{DEFAULT_METADATA_DIR}/database-types.json",
        "catalog_target": f"{target_catalog_dir}/{app_name}.json",
        "backup_dir": backup_dir,
        "version_override": version,
        "rollback": rollback,
    }
