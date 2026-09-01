from __future__ import annotations

import json
import shlex
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from libs import catalog
from libs.contentful import build_machine_fields, load_variables
from libs import remote
from libs.remote import resolve_secret_path as default_resolve_secret_path, scp_base, ssh_base, ssh_host as default_ssh_host, ssh_user as default_ssh_user
from libs.repo import repo_path

DEFAULT_REMOTE_USER = "root"
DEFAULT_CONTAINER = "websoft9"
DEFAULT_JSON_DIR = "/websoft9/media/json"
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


def distribution_for_app(app_name: str) -> list[dict]:
    variables = load_variables(app_name)
    return build_machine_fields(variables)["distribution"]


def _default_logo_url(app_name: str) -> str:
    return f"https://libs.websoft9.com/Websoft9/logo/product/{app_name}-websoft9.png"


def _build_screenshot_items(app_name: str, urls: list[str]) -> list[dict]:
    items = []
    for index, url in enumerate(urls, start=1):
        items.append({
            "id": f"{app_name}-screenshot-{index}",
            "key": f"screenshot-{index}",
            "value": url,
        })
    return items


def _build_catalog_collection(bindings: list[dict], taxonomy: dict) -> dict:
    if not bindings:
        return {"items": []}

    parent_meta = {
        category.get("key"): {
            "title": category.get("title"),
            "position": category.get("position"),
            "children": {child.get("key"): child.get("title") for child in category.get("children") or [] if child.get("key")},
        }
        for category in taxonomy.get("categories") or []
        if category.get("key")
    }

    grouped: dict[str, dict] = {}
    for binding in bindings:
        parent_key = binding["parentKey"]
        child_key = binding["childKey"]
        parent = parent_meta[parent_key]
        child_title = parent["children"][child_key]
        node = grouped.setdefault(
            child_key,
            {"key": child_key, "title": child_title, "catalogCollection": {"items": []}},
        )
        node["catalogCollection"]["items"].append(
            {"key": parent_key, "title": parent["title"], "position": parent["position"]}
        )
    return {"items": list(grouped.values())}


def build_product_entry(app_name: str) -> dict | None:
    repo_catalog = catalog.load_catalog(app_name)
    if not repo_catalog:
        return None

    variables = load_variables(app_name)
    machine = build_machine_fields(variables)
    taxonomy = catalog.load_taxonomy()
    bindings = catalog.validate_catalog_bindings(repo_catalog, taxonomy) if repo_catalog.get("catalogBindings") else []

    return {
        "key": machine["key"],
        "hot": None,
        "trademark": repo_catalog.get("trademark") or variables.get("trademark") or app_name,
        "summary": repo_catalog.get("summary", ""),
        "overview": repo_catalog.get("overview", ""),
        "websiteurl": repo_catalog.get("websiteurl") or ((variables.get("upstream") or {}).get("docs") or [""])[0],
        "description": repo_catalog.get("description", ""),
        "screenshots": _build_screenshot_items(app_name, repo_catalog.get("screenshots") or []),
        "distribution": machine["distribution"],
        "vcpu": machine["vcpu"],
        "memory": machine["memory"],
        "storage": machine["storage"],
        "logo": {"imageurl": repo_catalog.get("logoimageurl") or _default_logo_url(app_name)},
        "catalogCollection": _build_catalog_collection(bindings, taxonomy),
    }


def patch_product_entries(
    entries: list[dict],
    app_name: str,
    distribution: list[dict],
    product_entry: dict | None = None,
) -> tuple[list[dict] | None, list[dict], list[dict], bool]:
    updated = []
    before = None
    found = False
    for entry in entries:
        current = dict(entry)
        if current.get("key") == app_name:
            before = current.get("distribution")
            if product_entry is None:
                current["distribution"] = distribution
            else:
                current = dict(product_entry)
            found = True
        updated.append(current)
    if not found:
        updated.append({"key": app_name, "distribution": distribution} if product_entry is None else dict(product_entry))
        created = True
    else:
        created = False
    return before, distribution, updated, created


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
    remote = f"{user}@{host}"

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
        + ["-r", str(repo_path("apps", app_name)), f"{remote}:{staging_dir}/"],
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


def prepare_preview(
    app_name: str,
    host: str | None = None,
    user: str | None = None,
    secret_path: str | None = None,
    container: str = DEFAULT_CONTAINER,
    json_dir: str = DEFAULT_JSON_DIR,
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

    distribution = distribution_for_app(app_name)
    product_entry = build_product_entry(app_name)
    target_json_dir = json_dir.rstrip("/")
    deploy_dir = "/websoft9/library/apps"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backup_dir = f"/tmp/websoft9-appstore-sync-{app_name}-{timestamp}"

    total = 6

    _announce(progress, 1, total, "syncing app directory")
    _sync_app_dir(app_name, host, user, key_path, container, deploy_dir, backup_dir, progress=progress, verbose=verbose)

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        _announce(progress, 2, total, "backing up remote product JSON")
        _run(
            ssh_base(host, user, key_path)
            + [
                (
                    f"mkdir -p {backup_dir} && "
                    f"docker cp {container}:{target_json_dir}/product_en.json {backup_dir}/product_en.json.bak && "
                    f"docker cp {container}:{target_json_dir}/product_zh.json {backup_dir}/product_zh.json.bak"
                )
            ],
            progress=progress,
            verbose=verbose,
        )
        _announce(progress, 3, total, "downloading JSON backups")
        _run(
            scp_base(host, user, key_path)
            + [
                f"{user}@{host}:{backup_dir}/product_en.json.bak",
                f"{user}@{host}:{backup_dir}/product_zh.json.bak",
                str(tmp_dir),
            ],
            progress=progress,
            verbose=verbose,
        )

        before_en = None
        after_en = None
        created_en = False
        _announce(progress, 4, total, "patching product JSON locally")
        for name in ("product_en.json", "product_zh.json"):
            original = json.loads((tmp_dir / f"{name}.bak").read_text(encoding="utf-8"))
            before, after, updated, created = patch_product_entries(original, app_name, distribution, product_entry)
            (tmp_dir / name).write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if name == "product_en.json":
                before_en = before
                after_en = after
                created_en = created

        _announce(progress, 5, total, "uploading patched JSON files")
        _run(
            scp_base(host, user, key_path)
            + [
                str(tmp_dir / "product_en.json"),
                str(tmp_dir / "product_zh.json"),
                f"{user}@{host}:{backup_dir}/",
            ],
            progress=progress,
            verbose=verbose,
        )
        _announce(progress, 6, total, "applying patched JSON in container")
        _run(
            ssh_base(host, user, key_path)
            + [
                (
                    f"docker cp {backup_dir}/product_en.json {container}:{target_json_dir}/product_en.json && "
                    f"docker cp {backup_dir}/product_zh.json {container}:{target_json_dir}/product_zh.json"
                )
            ],
            progress=progress,
            verbose=verbose,
        )

    return {
        "app": app_name,
        "host": host,
        "user": user,
        "ssh_secret_path": str(key_path),
        "container": container,
        "json_dir": target_json_dir,
        "deploy_dir": deploy_dir,
        "app_target": f"{deploy_dir}/{app_name}",
        "created_entry": created_en,
        "backup_dir": backup_dir,
        "distribution_before": before_en,
        "distribution_after": after_en,
        "product_entry": product_entry,
        "rollback": [
            f"{_ssh_shell_prefix(key_path)} {user}@{host} 'if test -f {backup_dir}/{app_name}.tgz; then docker exec {container} sh -c \"rm -rf {deploy_dir}/{app_name}\" && docker exec -i {container} sh -c \"tar xzf - -C {deploy_dir}\" < {backup_dir}/{app_name}.tgz; fi'",
            f"{_ssh_shell_prefix(key_path)} {user}@{host} 'docker cp {backup_dir}/product_en.json.bak {container}:{target_json_dir}/product_en.json'",
            f"{_ssh_shell_prefix(key_path)} {user}@{host} 'docker cp {backup_dir}/product_zh.json.bak {container}:{target_json_dir}/product_zh.json'",
        ],
    }
