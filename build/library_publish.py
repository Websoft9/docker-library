#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT / "apps"
PACKAGE_ROOT_NAME = "library"
CHANNEL_PACKAGE_NAMES = {
    "dev": "library-dev.zip",
    "rc": "library-rc.zip",
    "release": "library-latest.zip",
}
V2_FULL_LATEST_NAME = "latest.zip"
CATALOG_FILE_NAMES = (
    "catalog_en.json",
    "catalog_zh.json",
    "product_en.json",
    "product_zh.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build appstore publish artifacts.")
    parser.add_argument("--channel", required=True, choices=sorted(CHANNEL_PACKAGE_NAMES))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--catalog-source-dir", required=True)
    parser.add_argument("--from-ref", default=None)
    parser.add_argument("--library-version", default=None)
    parser.add_argument("--all-apps", action="store_true", help="Build per-app packages for all apps (first-publish seed)")
    return parser.parse_args()


def run_git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_ref_exists(ref: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", ref],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def detect_from_ref(from_ref: str | None) -> str | None:
    if from_ref:
        if not git_ref_exists(from_ref):
            raise SystemExit(f"from-ref does not exist: {from_ref}")
        return from_ref
    if git_ref_exists("HEAD~1"):
        return "HEAD~1"
    return None


def format_dataset_version(dt: datetime) -> str:
    return dt.strftime("%Y.%m.%d.%H%M%S")


def resolve_from_version(from_ref: str | None) -> str:
    if not from_ref:
        return "initial"
    return run_git("rev-parse", "--short=16", from_ref)


def load_library_json(library_version: str | None) -> dict:
    with (ROOT / "library.json").open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if library_version:
        payload["Version"] = library_version
    elif not payload.get("Version"):
        payload["Version"] = format_dataset_version(datetime.now(timezone.utc))
    return payload


def write_json(path: Path, payload: object) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def load_variables_json(app_dir: Path) -> dict:
    path = app_dir / "variables.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def summarize_versions(edition_list: list[dict]) -> list[str]:
    versions: list[str] = []
    for edition in edition_list:
        for version in edition.get("version", []):
            if version not in versions:
                versions.append(version)
    return versions


APP_PACKAGE_NAME = "latest.zip"


def _hash_content(*contents: str) -> str:
    """Derive a short content-addressed version from one or more strings."""
    digest = hashlib.sha256()
    for c in contents:
        digest.update(c.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()[:16]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksum_file(path: Path) -> str:
    digest = sha256_file(path)
    checksum_path = path.with_name(f"{path.name}.sha256")
    checksum_path.write_text(f"{digest}  {path.name}\n", encoding="utf-8")
    return checksum_path.name


def create_zip_from_directory(source_dir: Path, destination_zip: Path) -> None:
    with ZipFile(destination_zip, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(path for path in source_dir.rglob("*") if path.is_file()):
            archive.write(path, arcname=path.relative_to(source_dir.parent))


def copy_package_contents(package_dir: Path, packaged_library_json: dict) -> None:
    for name in ("apps", "docs", "template"):
        source = ROOT / name
        if source.exists():
            shutil.copytree(source, package_dir / name)

    for markdown_file in sorted(ROOT.glob("*.md")):
        shutil.copy2(markdown_file, package_dir / markdown_file.name)

    write_json(package_dir / "library.json", packaged_library_json)


def copy_legacy_metadata(output_dir: Path, packaged_library_json: dict) -> dict:
    write_json(output_dir / "library.json", packaged_library_json)
    checksum_names = {
        "libraryMetadata": write_checksum_file(output_dir / "library.json"),
    }

    changelog_path = ROOT / "CHANGELOG.md"
    if changelog_path.exists():
        shutil.copy2(changelog_path, output_dir / "CHANGELOG.md")
        checksum_names["changelog"] = write_checksum_file(output_dir / "CHANGELOG.md")

    return checksum_names


def current_app_fingerprint(app_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(path for path in app_dir.rglob("*") if path.is_file()):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def build_app_package_entry(app_name: str) -> dict:
    return {"latest": f"apps/{app_name}/{APP_PACKAGE_NAME}"}


def build_app_checksum_entry(app_name: str) -> dict:
    return {"latest": f"apps/{app_name}/{APP_PACKAGE_NAME}.sha256"}


def build_apps_index(dataset_version: str, channel: str, generated_at: str) -> dict:
    apps = []
    for app_dir in sorted(path for path in APPS_DIR.iterdir() if path.is_dir()):
        variables = load_variables_json(app_dir)
        app_name = app_dir.name
        apps.append(
            {
                "app": app_name,
                "name": variables.get("name", app_name),
                "trademark": variables.get("trademark", variables.get("name", app_name)),
                "release": variables.get("release"),
                "versions": summarize_versions(variables.get("edition", [])),
                "path": f"apps/{app_name}",
                "hash": current_app_fingerprint(app_dir),
                "package": build_app_package_entry(app_name),
                "checksum": build_app_checksum_entry(app_name),
            }
        )

    return {
        "schemaVersion": "1",
        "datasetVersion": dataset_version,
        "channel": channel,
        "generatedAt": generated_at,
        "appCount": len(apps),
        "apps": apps,
    }


def apps_in_ref(from_ref: str | None) -> set[str]:
    if not from_ref:
        return set()

    output = run_git("ls-tree", "-r", "--name-only", from_ref, "apps")
    app_names: set[str] = set()
    for line in output.splitlines():
        parts = Path(line).parts
        if len(parts) >= 3 and parts[0] == "apps":
            app_names.add(parts[1])
    return app_names


def changed_apps_since(from_ref: str | None) -> set[str]:
    changed: set[str] = set()
    if from_ref:
        output = run_git("diff", "--name-only", from_ref, "--", "apps")
        for line in output.splitlines():
            parts = Path(line).parts
            if len(parts) >= 2 and parts[0] == "apps":
                changed.add(parts[1])

    status_output = run_git("status", "--porcelain", "--untracked-files=all", "--", "apps")
    for line in status_output.splitlines():
        candidate = line[3:].strip()
        parts = Path(candidate).parts
        if len(parts) >= 2 and parts[0] == "apps":
            changed.add(parts[1])
    return changed


def build_apps_delta(
    apps_index: dict,
    from_ref: str | None,
    from_version: str,
    to_version: str,
    channel: str,
    generated_at: str,
) -> dict:
    current_apps = {entry["app"] for entry in apps_index["apps"]}
    previous_apps = apps_in_ref(from_ref)

    added_apps = sorted(current_apps - previous_apps)
    removed_apps = sorted(previous_apps - current_apps)
    changed_apps = sorted(changed_apps_since(from_ref) - set(added_apps) - set(removed_apps))

    return {
        "schemaVersion": "1",
        "channel": channel,
        "fromRef": from_ref,
        "fromVersion": from_version,
        "toVersion": to_version,
        "generatedAt": generated_at,
        "addedApps": added_apps,
        "changedApps": changed_apps,
        "removedApps": removed_apps,
    }


def build_library_manifest(
    dataset_version: str,
    channel: str,
    full_package_names: dict,
    apps_index_name: str,
    apps_delta_name: str,
    checksum_names: dict,
    generated_at: str,
) -> dict:
    return {
        "schemaVersion": "1",
        "datasetVersion": dataset_version,
        "channel": channel,
        "fullPackage": full_package_names,
        "appsIndex": apps_index_name,
        "appsDelta": apps_delta_name,
        "appPackagesBase": "apps/",
        "supportsPartialUpdate": True,
        "checksum": checksum_names,
        "generatedAt": generated_at,
    }


def build_catalog_manifest(dataset_version: str, checksum_names: dict, generated_at: str, full_package_name: str) -> dict:
    return {
        "schemaVersion": "1",
        "datasetVersion": dataset_version,
        "source": "contentful",
        "fullPackage": full_package_name,
        "files": {
            "catalogEn": "catalog_en.json",
            "catalogZh": "catalog_zh.json",
            "productEn": "product_en.json",
            "productZh": "product_zh.json",
        },
        "checksum": checksum_names,
        "generatedAt": generated_at,
    }


def build_appstore_manifest(
    dataset_version: str, channel: str, generated_at: str,
    catalog_dsv: str, library_dsv: str,
) -> dict:
    return {
        "schemaVersion": "1",
        "datasetVersion": dataset_version,
        "channel": channel,
        "catalog": {
            "manifest": "catalog/manifest.json",
            "datasetVersion": catalog_dsv,
        },
        "library": {
            "manifest": "library/manifest.json",
            "datasetVersion": library_dsv,
        },
        "generatedAt": generated_at,
    }


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_distribution_map() -> dict[str, list[dict[str, object]]]:
    distribution_map: dict[str, list[dict[str, object]]] = {}
    for app_dir in sorted(path for path in APPS_DIR.iterdir() if path.is_dir()):
        variables = load_variables_json(app_dir)
        edition_list = variables.get("edition", [])
        if not edition_list:
            continue
        distribution_map[app_dir.name] = [
            {
                "key": edition.get("dist"),
                "value": edition.get("version", []),
            }
            for edition in edition_list
            if edition.get("dist")
        ]
    return distribution_map


def merge_product_distribution(product_entries: list[dict], distribution_map: dict[str, list[dict[str, object]]]) -> list[dict]:
    merged_entries: list[dict] = []
    for entry in product_entries:
        updated = dict(entry)
        distribution = distribution_map.get(updated.get("key"))
        if distribution:
            updated["distribution"] = distribution
        merged_entries.append(updated)
    return merged_entries


def ensure_catalog_source(source_dir: Path) -> dict[str, Path]:
    file_map: dict[str, Path] = {}
    for name in CATALOG_FILE_NAMES:
        path = source_dir / name
        if not path.exists():
            raise SystemExit(f"missing catalog source file: {path}")
        file_map[name] = path
    return file_map


def validate_legacy_media_artifacts(output_dir: Path, archive_name: str) -> None:
    if not (output_dir / archive_name).exists():
        raise SystemExit(f"missing legacy media archive: {archive_name}")
    if not (output_dir / f"{archive_name}.sha256").exists():
        raise SystemExit(f"missing legacy media checksum: {archive_name}.sha256")


def validate_catalog_artifacts(output_dir: Path, manifest: dict) -> None:
    for file_name in manifest["files"].values():
        if not (output_dir / file_name).exists():
            raise SystemExit(f"missing catalog artifact: {file_name}")
    for checksum_name in manifest["checksum"].values():
        if not (output_dir / checksum_name).exists():
            raise SystemExit(f"missing catalog checksum: {checksum_name}")
    if not (output_dir / "manifest.json").exists():
        raise SystemExit("missing catalog manifest.json")
    full_pkg = manifest.get("fullPackage")
    if full_pkg and not (output_dir / full_pkg).exists():
        raise SystemExit(f"missing catalog full package: {full_pkg}")


def validate_library_artifacts(output_dir: Path, manifest: dict, changed_app_names: set[str] | None = None) -> None:
    for name in (
        manifest["fullPackage"],
        manifest["appsIndex"],
        manifest["appsDelta"],
        "manifest.json",
    ):
        if not (output_dir / name).exists():
            raise SystemExit(f"missing library artifact: {name}")

    for checksum_name in manifest["checksum"].values():
        if not (output_dir / checksum_name).exists():
            raise SystemExit(f"missing library checksum: {checksum_name}")

    apps_delta = json.loads((output_dir / manifest["appsDelta"]).read_text(encoding="utf-8"))
    for key in ("addedApps", "changedApps", "removedApps"):
        if key not in apps_delta or not isinstance(apps_delta[key], list):
            raise SystemExit(f"invalid apps delta structure: {key}")

    apps_index = json.loads((output_dir / manifest["appsIndex"]).read_text(encoding="utf-8"))
    # Only validate per-app packages for apps that were actually (re)built
    # in this publish run.  Unchanged apps keep their existing packages on R2.
    validate_set = changed_app_names if changed_app_names is not None else {e["app"] for e in apps_index.get("apps", [])}

    for entry in apps_index.get("apps", []):
        if entry.get("app") not in validate_set:
            continue
        package = entry.get("package") or {}
        checksum = entry.get("checksum") or {}
        for path in (package.get("latest"), checksum.get("latest")):
            if not path or not (output_dir / path).exists():
                raise SystemExit(f"missing app package artifact: {entry.get('app')} -> {path}")


def validate_appstore_artifacts(appstore_dir: Path) -> None:
    required_paths = (
        appstore_dir / "catalog" / "manifest.json",
        appstore_dir / "library" / "manifest.json",
        appstore_dir / "manifests" / "appstore-manifest.json",
    )
    for path in required_paths:
        if not path.exists():
            raise SystemExit(f"missing appstore artifact: {path}")


def build_output_paths(base_output_dir: Path, channel: str) -> tuple[Path, Path]:
    legacy_library_dir = base_output_dir / "legacy" / channel / "library"
    v2_appstore_dir = base_output_dir / "appstore" / channel
    return legacy_library_dir, v2_appstore_dir


def build_legacy_library_artifacts(output_dir: Path, package_name: str, packaged_library_json: dict) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        package_dir = tmp_dir / PACKAGE_ROOT_NAME
        copy_package_contents(package_dir, packaged_library_json)
        create_zip_from_directory(package_dir, output_dir / package_name)

    checksum_names = {
        "libraryPackage": write_checksum_file(output_dir / package_name),
    }
    checksum_names.update(copy_legacy_metadata(output_dir, packaged_library_json))

    if package_name == "library-latest.zip":
        versioned_name = f"library-{packaged_library_json['Version']}.zip"
        shutil.copy2(output_dir / package_name, output_dir / versioned_name)
        checksum_names["libraryPackageVersioned"] = write_checksum_file(output_dir / versioned_name)
        checksum_names["libraryPackageLatest"] = checksum_names.pop("libraryPackage")

    return {
        "outputDir": str(output_dir),
        "libraryPackage": package_name,
        "version": packaged_library_json["Version"],
        "checksum": checksum_names,
    }


def build_legacy_media_artifacts(output_dir: Path, catalog_source_dir: Path, channel: str) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_name = "media-dev.zip" if channel == "dev" else "media-latest.zip"
    distribution_map = build_distribution_map() if channel == "dev" else {}

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        media_root = tmp_dir / "media"
        json_dir = media_root / "json"
        json_dir.mkdir(parents=True, exist_ok=True)

        catalog_sources = ensure_catalog_source(catalog_source_dir)

        for file_name, source_path in catalog_sources.items():
            destination = json_dir / file_name
            if file_name.startswith("product_") and distribution_map:
                product_entries = load_json(source_path)
                write_json(destination, merge_product_distribution(product_entries, distribution_map))
            else:
                shutil.copy2(source_path, destination)

        # Include logos and screenshots if workflow downloaded them
        for asset_dir in ("logos", "screenshots"):
            src = catalog_source_dir / asset_dir
            if src.is_dir():
                shutil.copytree(src, media_root / asset_dir)

        create_zip_from_directory(media_root, output_dir / archive_name)

    checksum_name = write_checksum_file(output_dir / archive_name)
    validate_legacy_media_artifacts(output_dir, archive_name)
    return {
        "outputDir": str(output_dir),
        "archive": archive_name,
        "checksum": checksum_name,
    }


def build_v2_appstore_artifacts(
    output_dir: Path,
    catalog_source_dir: Path,
    package_name: str,
    packaged_library_json: dict,
    dataset_version: str,
    from_ref: str | None,
    from_version: str,
    channel: str,
    generated_at: str,
    all_apps: bool = False,
) -> dict:
    catalog_dir = output_dir / "catalog"
    library_dir = output_dir / "library"
    manifests_dir = output_dir / "manifests"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    library_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    catalog_sources = ensure_catalog_source(catalog_source_dir)
    catalog_checksums: dict[str, str] = {}
    for file_name, source_path in catalog_sources.items():
        destination = catalog_dir / file_name
        shutil.copy2(source_path, destination)
        if file_name == "catalog_en.json":
            catalog_checksums["catalogEn"] = write_checksum_file(destination)
        elif file_name == "catalog_zh.json":
            catalog_checksums["catalogZh"] = write_checksum_file(destination)
        elif file_name == "product_en.json":
            catalog_checksums["productEn"] = write_checksum_file(destination)
        elif file_name == "product_zh.json":
            catalog_checksums["productZh"] = write_checksum_file(destination)

    catalog_checksum_values = ",".join(f"{k}={v}" for k, v in sorted(catalog_checksums.items()))
    catalog_dsv = _hash_content(catalog_checksum_values)

    # ── catalog full package ─────────────────────────────────
    catalog_full_dir = catalog_dir / "full"
    catalog_full_dir.mkdir(parents=True, exist_ok=True)
    catalog_zip_latest_name = V2_FULL_LATEST_NAME
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        for file_name in CATALOG_FILE_NAMES:
            shutil.copy2(catalog_dir / file_name, tmp_dir / file_name)
        create_zip_from_directory(tmp_dir, catalog_full_dir / catalog_zip_latest_name)
    catalog_checksums["fullPackage"] = f"full/{write_checksum_file(catalog_full_dir / catalog_zip_latest_name)}"

    catalog_manifest = build_catalog_manifest(
        catalog_dsv,
        catalog_checksums,
        generated_at,
        f"full/{catalog_zip_latest_name}",
    )
    write_json(catalog_dir / "manifest.json", catalog_manifest)
    write_checksum_file(catalog_dir / "manifest.json")
    validate_catalog_artifacts(catalog_dir, catalog_manifest)

    full_dir = library_dir / "full"
    apps_packages_dir = library_dir / "apps"
    full_dir.mkdir(parents=True, exist_ok=True)
    apps_packages_dir.mkdir(parents=True, exist_ok=True)

    # ── library – compute index & delta BEFORE per-app zips ──
    apps_index = build_apps_index(catalog_dsv, channel, generated_at)
    serialized_index = json.dumps(apps_index, sort_keys=True, ensure_ascii=False)
    library_dsv = _hash_content(serialized_index)
    full_latest_name = V2_FULL_LATEST_NAME

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        package_dir = tmp_dir / PACKAGE_ROOT_NAME
        copy_package_contents(package_dir, packaged_library_json)
        create_zip_from_directory(package_dir, full_dir / full_latest_name)

    apps_delta = build_apps_delta(
        apps_index=apps_index,
        from_ref=from_ref,
        from_version=from_version,
        to_version=library_dsv,
        channel=channel,
        generated_at=generated_at,
    )

    apps_index_name = f"apps-index-{library_dsv}.json"
    apps_delta_name = f"apps-delta-{from_version}-to-{library_dsv}.json"

    # Determine which apps actually need (re)built packages.
    # --all-apps (first-publish seed) or from_ref=None both mean "build everything".
    if all_apps or from_ref is None:
        changed_app_names: set[str] = {entry["app"] for entry in apps_index["apps"]}
    else:
        changed_app_names = set(apps_delta.get("addedApps", [])) | set(apps_delta.get("changedApps", []))

    # ── library – per-app packages (only for changed apps) ───
    for app_dir in sorted(path for path in APPS_DIR.iterdir() if path.is_dir()):
        app_name = app_dir.name
        if app_name not in changed_app_names:
            continue

        app_output_dir = apps_packages_dir / app_name
        app_output_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir = Path(tmp_dir_name)
            app_package_root = tmp_dir / app_name
            shutil.copytree(app_dir, app_package_root)
            create_zip_from_directory(app_package_root, app_output_dir / APP_PACKAGE_NAME)

        write_checksum_file(app_output_dir / APP_PACKAGE_NAME)

    # ── library – write index, delta, manifest ───────────────
    write_json(library_dir / apps_index_name, apps_index)
    write_json(library_dir / apps_delta_name, apps_delta)

    library_checksums = {
        "fullPackage": f"full/{write_checksum_file(full_dir / full_latest_name)}",
        "appsIndex": write_checksum_file(library_dir / apps_index_name),
        "appsDelta": write_checksum_file(library_dir / apps_delta_name),
    }

    library_manifest = build_library_manifest(
        dataset_version=library_dsv,
        channel=channel,
        full_package_names=f"full/{full_latest_name}",
        apps_index_name=apps_index_name,
        apps_delta_name=apps_delta_name,
        checksum_names=library_checksums,
        generated_at=generated_at,
    )
    write_json(library_dir / "manifest.json", library_manifest)
    write_checksum_file(library_dir / "manifest.json")
    validate_library_artifacts(library_dir, library_manifest, changed_app_names)

    appstore_dsv = _hash_content(catalog_dsv, library_dsv)
    appstore_manifest = build_appstore_manifest(appstore_dsv, channel, generated_at, catalog_dsv, library_dsv)
    write_json(manifests_dir / "appstore-manifest.json", appstore_manifest)
    appstore_manifest_checksum = write_checksum_file(manifests_dir / "appstore-manifest.json")
    validate_appstore_artifacts(output_dir)

    return {
        "outputDir": str(output_dir),
        "catalog": {
            "manifest": "catalog/manifest.json",
            "files": list(CATALOG_FILE_NAMES),
            "checksum": catalog_checksums,
            "datasetVersion": catalog_dsv,
        },
        "library": {
            "manifest": "library/manifest.json",
            "fullPackage": f"full/{full_latest_name}",
            "appPackagesBase": "apps/",
            "appsIndex": apps_index_name,
            "appsDelta": apps_delta_name,
            "checksum": library_checksums,
            "datasetVersion": library_dsv,
        },
        "appstore": {
            "manifest": "manifests/appstore-manifest.json",
            "checksum": appstore_manifest_checksum,
            "datasetVersion": appstore_dsv,
        },
    }


def main() -> int:
    args = parse_args()
    channel = args.channel
    output_root = Path(args.output_dir).resolve()
    catalog_source_dir = Path(args.catalog_source_dir).resolve()

    now = datetime.now(timezone.utc)
    generated_at = now.isoformat().replace("+00:00", "Z")
    dataset_version = format_dataset_version(now)
    from_ref = detect_from_ref(args.from_ref)
    from_version = resolve_from_version(from_ref)
    package_name = CHANNEL_PACKAGE_NAMES[channel]
    packaged_library_json = load_library_json(args.library_version or dataset_version)

    legacy_library_output_dir, v2_appstore_output_dir = build_output_paths(output_root, channel)
    legacy_media_output_dir = output_root / "legacy" / channel / "media"
    legacy_library_artifacts = build_legacy_library_artifacts(
        legacy_library_output_dir,
        package_name,
        packaged_library_json,
    )
    legacy_media_artifacts = build_legacy_media_artifacts(
        legacy_media_output_dir,
        catalog_source_dir,
        channel,
    )
    v2_appstore_artifacts = build_v2_appstore_artifacts(
        output_dir=v2_appstore_output_dir,
        catalog_source_dir=catalog_source_dir,
        package_name=package_name,
        packaged_library_json=packaged_library_json,
        dataset_version=dataset_version,
        from_ref=from_ref,
        from_version=from_version,
        channel=channel,
        generated_at=generated_at,
        all_apps=args.all_apps,
    )

    print(
        json.dumps(
            {
                "channel": channel,
                "datasetVersion": dataset_version,
                "fromRef": from_ref,
                "fromVersion": from_version,
                "legacy": {
                    "library": legacy_library_artifacts,
                    "media": legacy_media_artifacts,
                },
                "v2": v2_appstore_artifacts,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())