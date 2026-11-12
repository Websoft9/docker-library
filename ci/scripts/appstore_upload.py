#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal


RESTORE_HEADERS = (
    "CacheControl", "ContentDisposition", "ContentEncoding", "ContentLanguage",
    "ContentType", "Expires", "Metadata", "WebsiteRedirectLocation",
)


def upload_plan(output_dir: Path, channel: str) -> list[tuple[Path, str, dict]]:
    if channel not in {"dev", "rc", "release"}:
        raise ValueError("invalid Appstore channel")
    plan = []
    appstore = output_dir / "appstore" / channel
    for name in ("catalog", "library", "manifests"):
        directory = appstore / name
        if not directory.is_dir() or not any(directory.rglob("*")):
            raise ValueError(f"missing Appstore upload directory: {directory}")
        for source in sorted(directory.rglob("*")):
            if source.is_file():
                key = f"appstore/{channel}/{source.relative_to(appstore).as_posix()}"
                plan.append((source, key, {"CacheControl": "public, max-age=60"}))
    if channel == "dev":
        versions = appstore / "apps-verson.json"
        if not versions.is_file():
            raise ValueError("missing dev app version index")
        plan.append((versions, "appstore/dev/library/apps-verson.json", {"CacheControl": "public, max-age=60"}))
    def priority(entry: tuple[Path, str, dict]) -> tuple[int, str]:
        key = entry[1]
        if key == f"appstore/{channel}/manifests/appstore-manifest.json":
            return 4, key
        if key == f"appstore/{channel}/manifests/appstore-manifest.json.sha256":
            return 3, key
        if key in {f"appstore/{channel}/{name}/manifest.json" for name in ("catalog", "library")}:
            return 2, key
        if key in {f"appstore/{channel}/{name}/manifest.json.sha256" for name in ("catalog", "library")}:
            return 1, key
        return 0, key

    keys = {entry[1] for entry in plan}
    for key in (f"appstore/{channel}/catalog/manifest.json", f"appstore/{channel}/library/manifest.json",
                f"appstore/{channel}/manifests/appstore-manifest.json"):
        if key not in keys:
            raise ValueError(f"missing upload manifest: {key}")
        source = output_dir / key
        checksum = source.with_name(f"{source.name}.sha256")
        if not checksum.is_file():
            raise ValueError(f"missing upload manifest checksum: {key}.sha256")
        expected = f"{hashlib.sha256(source.read_bytes()).hexdigest()}  {source.name}"
        if checksum.read_text(encoding="utf-8").strip() != expected:
            raise ValueError(f"mismatched upload manifest checksum: {key}")
    return sorted(plan, key=priority)


def upload_artifacts(client, output_dir: Path, channel: str, backup_dir: Path, bucket: str = "artifact") -> int:
    plan = upload_plan(output_dir, channel)
    backup_dir.mkdir(parents=True, exist_ok=True)
    if any(backup_dir.iterdir()):
        raise ValueError("upload backup directory must be empty")
    backups = {}
    journal = []
    for position, (_, key, _) in enumerate(plan):
        try:
            head = client.head_object(Bucket=bucket, Key=key)
        except Exception as exc:
            code = str(getattr(exc, "response", {}).get("Error", {}).get("Code", ""))
            if code not in {"404", "NoSuchKey", "NotFound"}:
                raise
            backups[key] = None
            journal.append({"key": key, "existed": False})
        else:
            headers = {name: head[name] for name in RESTORE_HEADERS if name in head}
            backup = backup_dir / f"{position:06d}.object"
            client.download_file(bucket, key, str(backup))
            backups[key] = (backup, headers)
            journal.append({"key": key, "existed": True, "backup": backup.name, "headers": headers})
    (backup_dir / "journal.json").write_text(json.dumps({"bucket": bucket, "objects": journal}, indent=2, default=str) + "\n")

    attempted = []
    try:
        for source, key, headers in plan:
            attempted.append(key)
            client.upload_file(str(source), bucket, key, ExtraArgs=headers)
    except BaseException as upload_error:
        rollback_errors = []
        for key in reversed(attempted):
            try:
                previous = backups[key]
                if previous is None:
                    client.delete_object(Bucket=bucket, Key=key)
                else:
                    backup, headers = previous
                    client.upload_file(str(backup), bucket, key, ExtraArgs=headers)
            except Exception:
                rollback_errors.append(key)
        if rollback_errors:
            raise RuntimeError(f"Upload failed; rollback also failed for {rollback_errors}. Backup: {backup_dir}") from upload_error
        raise
    return len(plan)


def main() -> None:
    import boto3
    from botocore.config import Config

    parser = argparse.ArgumentParser(description="Upload Appstore objects with backup and failure rollback.")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--channel", required=True, choices=("dev", "rc", "release"))
    parser.add_argument("--backup-dir", required=True, type=Path)
    args = parser.parse_args()

    def interrupt(signum, frame):
        raise KeyboardInterrupt("Upload interrupted; attempting rollback")

    signal.signal(signal.SIGTERM, interrupt)
    client = boto3.client(
        "s3", endpoint_url=os.environ["AWS_ENDPOINT_URL"], region_name="auto",
        config=Config(request_checksum_calculation="when_required", response_checksum_validation="when_required"),
    )
    count = upload_artifacts(client, args.output_dir, args.channel, args.backup_dir)
    print(f"Published {count} Appstore objects in {args.channel}")


if __name__ == "__main__":
    main()