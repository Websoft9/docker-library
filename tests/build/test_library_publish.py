from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace

import pytest
import yaml

from _helpers import REPO_ROOT, load_build_module

library_publish = load_build_module("library_publish_test", REPO_ROOT / "ci" / "scripts" / "library_publish.py")
appstore_upload = load_build_module("appstore_upload_test", REPO_ROOT / "ci" / "scripts" / "appstore_upload.py")


def test_hash_content_is_deterministic_and_input_sensitive():
    assert library_publish._hash_content("a", "b") == library_publish._hash_content("a", "b")
    assert library_publish._hash_content("a") != library_publish._hash_content("b")
    assert len(library_publish._hash_content("a")) == 16


class FakeUploadError(Exception):
    def __init__(self, code):
        self.response = {"Error": {"Code": code}}


class FakeUploadStore:
    def __init__(self, objects=None, fail_key=None, backup_error=None, rollback_error=False):
        self.objects = dict(objects or {})
        self.fail_key = fail_key
        self.backup_error = backup_error
        self.rollback_error = rollback_error
        self.failed = False
        self.uploaded = []

    def head_object(self, Bucket, Key):
        if self.backup_error:
            raise FakeUploadError(self.backup_error)
        if Key not in self.objects:
            raise FakeUploadError("404")
        return self.objects[Key][1]

    def download_file(self, bucket, key, destination):
        Path(destination).write_bytes(self.objects[key][0])

    def upload_file(self, source, bucket, key, ExtraArgs):
        if self.failed and self.rollback_error:
            raise RuntimeError("simulated rollback failure")
        self.objects[key] = (Path(source).read_bytes(), ExtraArgs)
        self.uploaded.append(key)
        if key == self.fail_key and not self.failed:
            self.failed = True
            raise RuntimeError("simulated upload failure after mutation")

    def delete_object(self, Bucket, Key):
        if self.rollback_error:
            raise RuntimeError("simulated delete failure")
        self.objects.pop(Key, None)


@pytest.fixture
def upload_fixture(tmp_path):
    output = tmp_path / "upload"
    paths = (
        "appstore/dev/catalog/product_en.json", "appstore/dev/catalog/manifest.json",
        "appstore/dev/library/full/latest.zip", "appstore/dev/library/manifest.json",
        "appstore/dev/library/manifest.json.sha256", "appstore/dev/library/apps/demo/latest.zip",
        "appstore/dev/manifests/appstore-manifest.json.sha256", "appstore/dev/manifests/appstore-manifest.json",
        "appstore/dev/apps-verson.json", "legacy/dev/library/library-dev.zip", "legacy/dev/media/media-dev.zip",
    )
    for name in paths:
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"new")
    return output


def test_upload_commits_manifests_after_packages_and_preserves_unrelated_objects(upload_fixture, tmp_path):
    unrelated = {"appstore/dev/library/apps/unchanged/latest.zip": (b"old", {"CacheControl": "custom"})}
    client = FakeUploadStore(unrelated)
    plan = appstore_upload.upload_plan(upload_fixture, "dev")
    assert appstore_upload.upload_artifacts(client, upload_fixture, "dev", tmp_path / "backup") == len(plan)
    assert client.uploaded[-1] == "appstore/dev/manifests/appstore-manifest.json"
    assert client.uploaded.index("appstore/dev/library/apps/demo/latest.zip") < client.uploaded.index("appstore/dev/library/manifest.json")
    assert client.uploaded.index("dev/websoft9/plugin/media/media-dev.zip") < client.uploaded.index("appstore/dev/library/manifest.json")
    assert client.objects["appstore/dev/library/apps/unchanged/latest.zip"] == unrelated["appstore/dev/library/apps/unchanged/latest.zip"]
    assert client.objects["appstore/dev/library/apps-verson.json"][0] == b"new"


@pytest.mark.parametrize("first_publication", [False, True])
@pytest.mark.parametrize("failure_stage", ["data", "component", "root"])
def test_upload_failure_restores_bytes_headers_and_removes_new_objects(upload_fixture, tmp_path, first_publication, failure_stage):
    fail_key = {"data": "appstore/dev/library/full/latest.zip", "component": "appstore/dev/library/manifest.json",
                "root": "appstore/dev/manifests/appstore-manifest.json"}[failure_stage]
    plan = appstore_upload.upload_plan(upload_fixture, "dev")
    original = {} if first_publication else {
        key: (b"old", {"CacheControl": "private", "ContentType": "application/zip", "Metadata": {"owner": "original"}})
        for _, key, _ in plan if not key.endswith("apps-verson.json")
    }
    client = FakeUploadStore(original, fail_key=fail_key)
    with pytest.raises(RuntimeError, match="simulated upload failure"):
        appstore_upload.upload_artifacts(client, upload_fixture, "dev", tmp_path / "backup")
    assert client.objects == original


@pytest.mark.parametrize("code", ["403", "500"])
def test_upload_backup_errors_prevent_all_writes(upload_fixture, tmp_path, code):
    client = FakeUploadStore(backup_error=code)
    with pytest.raises(FakeUploadError):
        appstore_upload.upload_artifacts(client, upload_fixture, "dev", tmp_path / "backup")
    assert client.uploaded == []


def test_upload_backup_download_failure_prevents_all_writes(upload_fixture, tmp_path, monkeypatch):
    plan = appstore_upload.upload_plan(upload_fixture, "dev")
    client = FakeUploadStore({key: (b"old", {}) for _, key, _ in plan})

    def fail_download(*args):
        raise RuntimeError("simulated backup download failure")

    monkeypatch.setattr(client, "download_file", fail_download)
    with pytest.raises(RuntimeError, match="backup download failure"):
        appstore_upload.upload_artifacts(client, upload_fixture, "dev", tmp_path / "backup")
    assert client.uploaded == []


def test_upload_interrupt_restores_existing_objects(upload_fixture, tmp_path, monkeypatch):
    plan = appstore_upload.upload_plan(upload_fixture, "dev")
    original = {key: (b"old", {}) for _, key, _ in plan}
    client = FakeUploadStore(original)
    upload_file = client.upload_file
    interrupted = False

    def interrupt_upload(*args, **kwargs):
        nonlocal interrupted
        upload_file(*args, **kwargs)
        if not interrupted:
            interrupted = True
            raise KeyboardInterrupt("simulated interruption")

    monkeypatch.setattr(client, "upload_file", interrupt_upload)
    with pytest.raises(KeyboardInterrupt, match="simulated interruption"):
        appstore_upload.upload_artifacts(client, upload_fixture, "dev", tmp_path / "backup")
    assert client.objects == original


def test_failed_rollback_is_reported_and_keeps_backup(upload_fixture, tmp_path):
    key = "appstore/dev/library/full/latest.zip"
    client = FakeUploadStore({key: (b"old", {"ContentType": "application/zip"})}, fail_key=key, rollback_error=True)
    backup = tmp_path / "backup"
    with pytest.raises(RuntimeError, match="rollback also failed"):
        appstore_upload.upload_artifacts(client, upload_fixture, "dev", backup)
    journal = json.loads((backup / "journal.json").read_text())
    entry = next(entry for entry in journal["objects"] if entry["key"] == key)
    assert (backup / entry["backup"]).read_bytes() == b"old"


@pytest.mark.parametrize("channel", ["rc", "release"])
def test_upload_keeps_channel_and_legacy_paths(upload_fixture, tmp_path, channel):
    (upload_fixture / "appstore/dev").rename(upload_fixture / "appstore" / channel)
    (upload_fixture / "legacy/dev").rename(upload_fixture / "legacy" / channel)
    client = FakeUploadStore()
    appstore_upload.upload_artifacts(client, upload_fixture, channel, tmp_path / "backup")
    assert client.uploaded[-1] == f"appstore/{channel}/manifests/appstore-manifest.json"
    assert all(key.startswith((f"appstore/{channel}/", f"{channel}/websoft9/")) for key in client.uploaded)
    assert not any(key.endswith("apps-verson.json") for key in client.uploaded)


def test_workflow_uses_one_rollback_upload_before_purge_and_keeps_recovery_backup():
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/appstore-publish.yml").read_text())
    steps = workflow["jobs"]["publish"]["steps"]
    upload = next(step for step in steps if step.get("id") == "upload_appstore")
    assert "ci/scripts/appstore_upload.py" in upload["run"]
    assert "--backup-dir dist/appstore-upload-backup" in upload["run"]
    assert not any("aws s3 sync" in step.get("run", "") and "s3://artifact/" in step["run"] for step in steps)
    recovery = next(step for step in steps if step.get("name") == "Preserve failed upload recovery backup")
    assert "steps.upload_appstore.outcome == 'failure'" in recovery["if"]
    purge = next(step for step in steps if step.get("name") == "Purge legacy Cloudflare Cache")
    assert steps.index(upload) < steps.index(purge)


def test_upload_cli_uses_configured_client_without_sdk_or_network(upload_fixture, tmp_path, monkeypatch, capsys):
    client = FakeUploadStore()
    captured = {}

    def create_client(service, **kwargs):
        captured.update(service=service, **kwargs)
        return client

    boto3 = ModuleType("boto3")
    boto3.client = create_client
    config = ModuleType("botocore.config")
    config.Config = lambda **kwargs: kwargs
    monkeypatch.setitem(sys.modules, "boto3", boto3)
    monkeypatch.setitem(sys.modules, "botocore", ModuleType("botocore"))
    monkeypatch.setitem(sys.modules, "botocore.config", config)
    monkeypatch.setenv("AWS_ENDPOINT_URL", "https://mock.invalid")
    monkeypatch.setattr(sys, "argv", [
        "appstore_upload.py", "--output-dir", str(upload_fixture), "--channel", "dev",
        "--backup-dir", str(tmp_path / "backup"),
    ])
    handlers = {}
    monkeypatch.setattr(appstore_upload.signal, "signal", lambda signum, handler: handlers.update({signum: handler}))

    appstore_upload.main()

    assert captured == {
        "service": "s3", "endpoint_url": "https://mock.invalid", "region_name": "auto",
        "config": {"request_checksum_calculation": "when_required", "response_checksum_validation": "when_required"},
    }
    assert client.uploaded[-1] == "appstore/dev/manifests/appstore-manifest.json"
    assert f"Published {len(client.uploaded)} Appstore objects in dev" in capsys.readouterr().out
    with pytest.raises(KeyboardInterrupt, match="attempting rollback"):
        handlers[appstore_upload.signal.SIGTERM](appstore_upload.signal.SIGTERM, None)


def test_to_utc_z_normalizes_offsets():
    assert library_publish.to_utc_z("2022-11-29T10:49:58+08:00") == "2022-11-29T02:49:58Z"
    assert library_publish.to_utc_z("2026-09-20T09:52:48Z") == "2026-09-20T09:52:48Z"


def test_build_app_updated_at_map_keeps_latest_per_app(monkeypatch):
    output = "\n".join(
        [
            "@@2026-09-20T09:52:48Z",
            "apps/alpha/docker-compose.yml",
            "apps/beta/README.md",
            "@@2026-08-01T00:00:00+08:00",
            "apps/alpha/.env",
        ]
    )
    monkeypatch.setattr(library_publish, "run_git", lambda *args, **kwargs: output)

    mapping = library_publish.build_app_updated_at_map()

    assert mapping["alpha"] == "2026-09-20T09:52:48Z"
    assert mapping["beta"] == "2026-09-20T09:52:48Z"


def test_compute_catalog_dataset_version_is_content_sensitive(tmp_path: Path):
    catalog_dir = tmp_path / "catalog"
    catalog_dir.mkdir()
    for file_name in library_publish.CATALOG_FILE_NAMES:
        (catalog_dir / file_name).write_text("[]\n", encoding="utf-8")

    baseline = library_publish.compute_catalog_dataset_version(catalog_dir)
    assert len(baseline) == 16
    assert baseline == library_publish.compute_catalog_dataset_version(catalog_dir)

    (catalog_dir / "product_en.json").write_text('[{"key": "lobechat"}]\n', encoding="utf-8")
    changed = library_publish.compute_catalog_dataset_version(catalog_dir)

    assert changed != baseline


def test_summarize_versions_deduplicates_and_preserves_order():
    editions = [
        {"dist": "community", "version": ["1.0", "1.0", "2.0"]},
        {"dist": "enterprise", "version": ["9.9"]},
    ]

    assert library_publish.summarize_versions(editions) == ["1.0", "2.0", "9.9"]


def test_build_apps_version_summary_preserves_all_versions_per_app(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")

    assert library_publish.build_apps_version_summary() == [{"id": "demo", "version": ["1.0", "latest"]}]


def test_app_package_and_checksum_entry_shapes():
    assert library_publish.build_app_package_entry("demo") == {"latest": "apps/demo/latest.zip"}
    assert library_publish.build_app_checksum_entry("demo") == {"latest": "apps/demo/latest.zip.sha256"}


def test_apps_index_dataset_version_describes_its_own_content(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)

    index, dataset_version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")

    assert index["datasetVersion"] == dataset_version
    assert len(dataset_version) == 16

    body = {key: value for key, value in index.items() if key not in {"datasetVersion", "generatedAt", "apps"}}
    body["apps"] = [{key: value for key, value in app.items() if key != "updatedAt"} for app in index["apps"]]
    expected = library_publish._hash_content(json.dumps(body, sort_keys=True, ensure_ascii=False))
    assert dataset_version == expected


def test_apps_index_version_ignores_publication_and_display_times(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    before, old_version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")
    after, new_version = library_publish.build_apps_index_with_version(
        "dev", "2026-02-01T00:00:00Z", {"demo": "2026-01-31T00:00:00Z"},
    )

    assert old_version == new_version
    assert before["generatedAt"] != after["generatedAt"]
    assert before["apps"][0]["updatedAt"] != after["apps"][0]["updatedAt"]
    (build_fixture / "apps" / "demo" / ".env").write_text("CHANGED=yes\n")
    assert library_publish.build_apps_index_with_version("dev", "2026-02-01T00:00:00Z")[1] != old_version


@pytest.mark.parametrize("schema_version", ["1", "2"])
def test_previous_published_index_supplies_dataset_version(build_fixture, monkeypatch, schema_version):
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    index, version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")
    index["schemaVersion"] = schema_version
    if schema_version == "1":
        index.pop("metadata")
    path = build_fixture / "previous.json"
    path.write_text(json.dumps(index))

    assert library_publish.load_previous_apps_index(str(path), "dev") == index
    assert library_publish.resolve_from_version(index) == version
    assert library_publish.resolve_from_version(None) == "initial"
    with pytest.raises(SystemExit, match="invalid previous apps index"):
        library_publish.load_previous_apps_index(str(path), "release")
    index["apps"].append(index["apps"][0])
    path.write_text(json.dumps(index))
    with pytest.raises(SystemExit, match="application identity"):
        library_publish.load_previous_apps_index(str(path), "dev")


@pytest.mark.parametrize("schema_version", ["3", 1, None, [], {}])
def test_previous_published_index_rejects_unknown_schema(build_fixture, monkeypatch, schema_version):
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    index, _ = library_publish.build_apps_index_with_version("release", "2026-01-01T00:00:00Z")
    index["schemaVersion"] = schema_version
    path = build_fixture / "previous.json"
    path.write_text(json.dumps(index))

    with pytest.raises(SystemExit, match="invalid previous apps index"):
        library_publish.load_previous_apps_index(str(path), "release")


def test_published_delta_compares_fingerprints_not_git_history(monkeypatch):
    previous = {"apps": [{"app": "changed", "hash": "old"}, {"app": "removed", "hash": "old"}, {"app": "same", "hash": "same"}]}
    current = {"apps": [{"app": "changed", "hash": "new"}, {"app": "added", "hash": "new"}, {"app": "same", "hash": "same"}]}
    monkeypatch.setattr(library_publish, "run_git", lambda *args: pytest.fail("must use the published snapshot"))

    delta = library_publish.build_apps_delta(current, "HEAD~1", "previous-version", "next-version", "dev", "now", previous)

    assert delta["addedApps"] == ["added"]
    assert delta["changedApps"] == ["changed"]
    assert delta["removedApps"] == ["removed"]


@pytest.mark.parametrize("scenario", ["first", "existing", "corrupt", "unavailable"])
def test_workflow_downloads_verified_published_baseline(tmp_path, scenario):
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/appstore-publish.yml").read_text())
    step = next(step for step in workflow["jobs"]["publish"]["steps"] if step.get("id") == "check_seed")
    index = {"datasetVersion": "a" * 16, "channel": "dev", "apps": []}
    source = tmp_path / "source"
    source.mkdir()
    index_path = source / f"apps-index-{index['datasetVersion']}.json"
    index_path.write_text(json.dumps(index))
    library_publish.write_checksum_file(index_path)
    if scenario == "corrupt":
        index_path.write_text("corrupted")
    (source / "appstore-manifest.json").write_text(json.dumps({"library": {"datasetVersion": index["datasetVersion"]}}))
    executable_dir = tmp_path / "bin"
    executable_dir.mkdir()
    executable = executable_dir / "aws"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import os, pathlib, shutil, sys\n"
        "scenario = os.environ['SCENARIO']\n"
        "if scenario == 'unavailable': sys.exit(42)\n"
        "if sys.argv[1] == 's3api':\n"
        "    print('None' if scenario == 'first' else 'appstore/dev/manifests/appstore-manifest.json')\n"
        "else:\n"
        "    shutil.copyfile(pathlib.Path(os.environ['SOURCE']) / sys.argv[3].rsplit('/', 1)[-1], sys.argv[4])\n"
    )
    executable.chmod(0o755)
    output = tmp_path / "outputs"
    env = dict(os.environ, PATH=f"{executable_dir}:{os.environ['PATH']}", CHANNEL="dev",
               AWS_ENDPOINT_URL="https://unused.invalid", GITHUB_OUTPUT=str(output),
               SCENARIO=scenario, SOURCE=str(source))

    result = subprocess.run(["bash", "-c", step["run"]], cwd=tmp_path, env=env, capture_output=True, text=True)

    if scenario in {"corrupt", "unavailable"}:
        assert result.returncode != 0
        assert not output.exists()
    else:
        assert result.returncode == 0, result.stderr
        outputs = dict(line.split("=", 1) for line in output.read_text().splitlines())
        assert outputs["seed"] == ("true" if scenario == "first" else "false")
        if scenario == "existing":
            assert json.loads(Path(outputs["index_path"]).read_text()) == index


def test_build_apps_index_with_fixture_apps(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)

    index = library_publish.build_apps_index("dev", "2026-01-01T00:00:00Z")

    assert index["schemaVersion"] == "1"
    assert "datasetVersion" not in index
    assert index["appCount"] == 1
    entry = index["apps"][0]
    assert entry["app"] == "demo"
    assert entry["name"] == "demo"
    assert entry["trademark"] == "Demo App"
    assert entry["release"] is True
    assert entry["versions"] == ["1.0", "latest"]
    assert entry["path"] == "apps/demo"
    assert entry["updatedAt"] == "2026-01-01T00:00:00Z"
    assert entry["package"] == {"latest": "apps/demo/latest.zip"}
    assert entry["checksum"] == {"latest": "apps/demo/latest.zip.sha256"}
    assert len(entry["hash"]) == 64


def test_build_apps_index_uses_provided_updated_at(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)

    index = library_publish.build_apps_index("dev", "2026-01-01T00:00:00Z", {"demo": "2026-05-05T00:00:00Z"})

    assert index["apps"][0]["updatedAt"] == "2026-05-05T00:00:00Z"


def test_build_apps_delta_computes_added_changed_removed(monkeypatch):
    apps_index = {"apps": [{"app": "b"}, {"app": "c"}]}
    monkeypatch.setattr(library_publish, "apps_in_ref", lambda from_ref: {"a", "c"})
    monkeypatch.setattr(library_publish, "changed_apps_since", lambda from_ref: {"b", "c"})

    delta = library_publish.build_apps_delta(
        apps_index=apps_index,
        from_ref="HEAD~1",
        from_version="abc",
        to_version="def",
        channel="dev",
        generated_at="2026-01-01T00:00:00Z",
    )

    assert delta["addedApps"] == ["b"]
    assert delta["removedApps"] == ["a"]
    assert delta["changedApps"] == ["c"]
    assert delta["schemaVersion"] == "1"


def test_distribution_map_and_merge_product_distribution(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")

    distribution_map = library_publish.build_distribution_map()

    assert distribution_map == {"demo": [{"key": "community", "value": ["1.0", "latest"]}]}

    merged = library_publish.merge_product_distribution(
        [{"key": "demo", "title": "Demo"}, {"key": "other", "title": "Other"}],
        distribution_map,
    )
    assert merged[0]["distribution"] == [{"key": "community", "value": ["1.0", "latest"]}]
    assert "distribution" not in merged[1]


def test_zip_and_checksum_round_trip(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("hello\n", encoding="utf-8")
    (source / "nested").mkdir(parents=True, exist_ok=True)
    (source / "nested" / "b.txt").write_text("world\n", encoding="utf-8")

    zip_path = tmp_path / "package.zip"
    library_publish.create_zip_from_directory(source, zip_path)
    checksum_name = library_publish.write_checksum_file(zip_path)
    checksum_path = tmp_path / checksum_name

    import zipfile

    with zipfile.ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == ["source/a.txt", "source/nested/b.txt"]

    digest = library_publish.sha256_file(zip_path)
    assert checksum_path.read_text(encoding="utf-8") == f"{digest}  package.zip\n"


def test_manifest_builders_have_expected_shape():
    catalog = library_publish.build_catalog_manifest(
        "c-dsv", {"catalogEn": "catalog_en.json.sha256"}, "2026-01-01T00:00:00Z", "full/latest.zip"
    )
    assert catalog["schemaVersion"] == "1"
    assert catalog["source"] == "contentful"
    assert catalog["files"]["catalogEn"] == "catalog_en.json"
    assert catalog["fullPackage"] == "full/latest.zip"

    library = library_publish.build_library_manifest(
        "l-dsv", "dev", "full/latest.zip", "apps-index.json", "apps-delta.json", {"fullPackage": "x.sha256"}, "2026-01-01T00:00:00Z"
    )
    assert library["schemaVersion"] == "1"
    assert library["supportsPartialUpdate"] is True
    assert library["appPackagesBase"] == "apps/"

    appstore = library_publish.build_appstore_manifest(
        "a-dsv", "dev", "2026-01-01T00:00:00Z", "c-dsv", "l-dsv"
    )
    assert appstore["minWebsoft9Version"] == library_publish.MIN_WEBSOFT9_VERSION
    assert appstore["catalog"]["manifest"] == "catalog/manifest.json"
    assert appstore["library"] == {"manifest": "library/manifest.json", "datasetVersion": "l-dsv"}
    assert appstore["schemaVersion"] == "1"


def test_ensure_catalog_source_requires_all_four_files(tmp_path: Path):
    source_dir = tmp_path / "catalog"
    source_dir.mkdir()
    (source_dir / "catalog_en.json").write_text("[]\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="missing catalog source file"):
        library_publish.ensure_catalog_source(source_dir)


def test_validate_catalog_artifacts_rejects_missing_files(tmp_path: Path):
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    manifest = {
        "files": {"catalogEn": "catalog_en.json"},
        "checksum": {"catalogEn": "catalog_en.json.sha256"},
        "fullPackage": "full/latest.zip",
    }

    with pytest.raises(SystemExit, match="missing catalog artifact"):
        library_publish.validate_catalog_artifacts(output_dir, manifest)


def test_release_metadata_uses_tag_without_source_version_file(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    assert not (build_fixture / "library.json").exists()
    assert library_publish.build_library_metadata("release", "2.0.0") == {"Version": "2.0.0", "schemaVersion": "1"}


@pytest.mark.parametrize("value", [None, "", "v2.0.0", "2.0", "2.0.0-rc.1", "02.0.0", "../2.0.0"])
def test_release_metadata_rejects_missing_or_nonstable_versions(value):
    with pytest.raises(SystemExit, match="stable X.Y.Z tag"):
        library_publish.build_library_metadata("release", value)


@pytest.mark.parametrize("channel", ["dev", "rc"])
def test_nonrelease_metadata_defaults_to_commit_version(channel, monkeypatch):
    monkeypatch.setattr(library_publish, "run_git", lambda *args: "abcdef123456")
    assert library_publish.build_library_metadata(channel, None) == {"Version": f"{channel}-abcdef123456", "schemaVersion": "1"}


def test_release_packages_embed_generated_metadata_without_source_file(build_fixture, monkeypatch):
    from zipfile import ZipFile

    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    metadata = library_publish.build_library_metadata("release", "2.0.0")
    output = build_fixture / "output"
    result = library_publish.build_legacy_library_artifacts(output, "library-latest.zip", metadata)

    assert not (build_fixture / "library.json").exists()
    assert result["version"] == "2.0.0"
    assert json.loads((output / "library.json").read_text()) == metadata
    assert (output / "library-2.0.0.zip").read_bytes() == (output / "library-latest.zip").read_bytes()
    with ZipFile(output / "library-latest.zip") as archive:
        assert json.loads(archive.read("library/library.json")) == metadata


def test_main_orchestrates_publish_steps(monkeypatch, tmp_path, capsys):
    args = SimpleNamespace(
        channel="dev",
        output_dir=str(tmp_path / "out"),
        catalog_source_dir=str(tmp_path / "catalog"),
        from_ref=None,
        library_version="1.0.0",
        all_apps=False,
    )
    monkeypatch.setattr(library_publish, "parse_args", lambda: args)
    monkeypatch.setattr(library_publish, "detect_from_ref", lambda from_ref: None)
    monkeypatch.setattr(library_publish, "resolve_from_version", lambda from_ref: "initial")
    monkeypatch.setattr(library_publish, "format_dataset_version", lambda dt: "2026.01.01.000000")
    monkeypatch.setattr(library_publish, "build_output_paths", lambda output_root, channel: (tmp_path / "legacy", tmp_path / "v2"))
    monkeypatch.setattr(library_publish, "build_legacy_library_artifacts", lambda *args, **kwargs: {"kind": "legacy-library"})
    monkeypatch.setattr(library_publish, "build_legacy_media_artifacts", lambda *args, **kwargs: {"kind": "legacy-media"})
    monkeypatch.setattr(library_publish, "build_v2_appstore_artifacts", lambda *args, **kwargs: {"kind": "v2"})

    assert library_publish.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["channel"] == "dev"
    assert payload["fromRef"] is None
    assert payload["legacy"] == {"library": {"kind": "legacy-library"}, "media": {"kind": "legacy-media"}}
    assert payload["v2"] == {"kind": "v2"}


@pytest.mark.parametrize("channel", ["dev", "rc", "release"])
def test_full_publish_without_source_library_json(build_fixture, monkeypatch, capsys, channel):
    from zipfile import ZipFile

    catalog = build_fixture / "catalog-source"
    catalog.mkdir()
    for filename in library_publish.CATALOG_FILE_NAMES:
        (catalog / filename).write_text("[]\n")
    output = build_fixture / "output"
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(library_publish, "detect_from_ref", lambda ref: None)
    monkeypatch.setattr(library_publish, "run_git", lambda *args: "abcdef123456" if args[0] == "rev-parse" else "")
    monkeypatch.setattr(library_publish, "parse_args", lambda: SimpleNamespace(
        channel=channel, output_dir=str(output), catalog_source_dir=str(catalog),
        from_ref=None, library_version="2.0.0" if channel == "release" else None, all_apps=False,
    ))

    assert library_publish.main() == 0
    capsys.readouterr()
    expected = {"Version": "2.0.0" if channel == "release" else f"{channel}-abcdef123456", "schemaVersion": "1"}
    assert not (build_fixture / "library.json").exists()
    assert json.loads((output / "legacy" / channel / "library" / "library.json").read_text()) == expected
    with ZipFile(output / "appstore" / channel / "library" / "full" / "latest.zip") as archive:
        assert json.loads(archive.read("library/library.json")) == expected
        assert archive.read("library/metadata/database-types.json") == (build_fixture / "metadata" / "database-types.json").read_bytes()
        assert archive.read("library/metadata/secret-rules.json") == (build_fixture / "metadata" / "secret-rules.json").read_bytes()
    library_dir = output / "appstore" / channel / "library"
    manifest = json.loads((library_dir / "manifest.json").read_text())
    assert manifest["schemaVersion"] == "1"
    assert manifest["supportsPartialUpdate"] is False
    dictionary = manifest["metadata"]["databaseTypes"]
    assert library_publish.sha256_file(library_dir / dictionary["path"]) == dictionary["sha256"]
    assert (library_dir / manifest["checksum"]["databaseTypes"]).is_file()
    secret_rules = manifest["metadata"]["secretRules"]
    assert library_publish.sha256_file(library_dir / secret_rules["path"]) == secret_rules["sha256"]
    assert (library_dir / manifest["checksum"]["secretRules"]).is_file()
    assert (output / "appstore" / channel / "library" / "apps" / "demo" / "latest.zip").exists()
    versions_path = output / "appstore" / channel / "apps-verson.json"
    if channel == "dev":
        assert json.loads(versions_path.read_text()) == [{"id": "demo", "version": ["1.0", "latest"]}]
    else:
        assert not versions_path.exists()


@pytest.mark.parametrize("filename,metadata_key,profile,field,value", [
    ("database-types.json", "databaseTypes", "postgresql", "port", 5433),
    ("secret-rules.json", "secretRules", "base64", "description", "Updated generation profile."),
])
def test_dictionary_only_change_updates_dataset_without_changing_app_hash(
    build_fixture, monkeypatch, filename, metadata_key, profile, field, value,
):
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    baseline, old_version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")
    path = build_fixture / "metadata" / filename
    definitions = json.loads(path.read_text())
    definitions[profile][field] = value
    path.write_text(json.dumps(definitions))
    current, new_version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")
    assert old_version != new_version
    assert baseline["apps"] == current["apps"]
    assert baseline["metadata"][metadata_key] != current["metadata"][metadata_key]


@pytest.mark.parametrize("schema_version", ["1", "2"])
@pytest.mark.parametrize("filename,metadata_key,profile,field,value", [
    ("database-types.json", "databaseTypes", "postgresql", "port", 5433),
    ("secret-rules.json", "secretRules", "base64", "description", "Updated generation profile."),
])
def test_dictionary_only_increment_delivers_shared_file_without_rebuilding_apps(
    build_fixture, monkeypatch, schema_version, filename, metadata_key, profile, field, value,
):
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(library_publish, "apps_in_ref", lambda ref: {"demo"})
    monkeypatch.setattr(library_publish, "changed_apps_since", lambda ref: set())
    monkeypatch.setattr(library_publish, "build_app_updated_at_map", lambda: {})
    previous, previous_version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")
    previous["schemaVersion"] = schema_version
    dictionary = build_fixture / "metadata" / filename
    definitions = json.loads(dictionary.read_text())
    definitions[profile][field] = value
    dictionary.write_text(json.dumps(definitions))
    catalog = build_fixture / "catalog-source"
    catalog.mkdir()
    for filename in library_publish.CATALOG_FILE_NAMES:
        (catalog / filename).write_text("[]\n")
    output = build_fixture / "incremental"
    result = library_publish.build_v2_appstore_artifacts(
        output, catalog, "library-dev.zip", {"Version": "dev-test", "schemaVersion": "1"},
        "unused", "previous", "previous-version", "dev", "2026-01-01T00:00:00Z",
        previous_apps_index=previous,
    )
    manifest = json.loads((output / "library" / "manifest.json").read_text())
    assert manifest["schemaVersion"] == "1"
    assert manifest["supportsPartialUpdate"] is True
    assert manifest["datasetVersion"] != previous_version
    entry = manifest["metadata"][metadata_key]
    assert (output / "library" / entry["path"]).is_file()
    assert not list((output / "library" / "apps").rglob("*.zip"))
    delta = json.loads((output / "library" / result["library"]["appsDelta"]).read_text())
    assert delta["schemaVersion"] == "1"
    assert delta["fromVersion"] == previous_version
    assert delta["toVersion"] == manifest["datasetVersion"]
    assert delta["addedApps"] == delta["changedApps"] == delta["removedApps"] == []
    (output / "library" / entry["path"]).write_text("corrupted")
    with pytest.raises(SystemExit, match="mismatched shared"):
        library_publish.validate_library_artifacts(output / "library", manifest, set())
