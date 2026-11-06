from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml

from _helpers import REPO_ROOT, load_build_module

library_publish = load_build_module("library_publish_test", REPO_ROOT / "ci" / "scripts" / "library_publish.py")


def test_hash_content_is_deterministic_and_input_sensitive():
    assert library_publish._hash_content("a", "b") == library_publish._hash_content("a", "b")
    assert library_publish._hash_content("a") != library_publish._hash_content("b")
    assert len(library_publish._hash_content("a")) == 16


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


def test_build_apps_version_summary_uses_first_version_per_app(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")

    assert library_publish.build_apps_version_summary() == [{"id": "demo", "version": "1.0"}]


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
    assert appstore["library"]["manifest"] == "library/manifest.json"
    assert appstore["schemaVersion"] == appstore["library"]["schemaVersion"] == "1"


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
    library_dir = output / "appstore" / channel / "library"
    manifest = json.loads((library_dir / "manifest.json").read_text())
    assert manifest["schemaVersion"] == "1"
    assert manifest["supportsPartialUpdate"] is False
    dictionary = manifest["metadata"]["databaseTypes"]
    assert library_publish.sha256_file(library_dir / dictionary["path"]) == dictionary["sha256"]
    assert (library_dir / manifest["checksum"]["databaseTypes"]).is_file()
    assert (output / "appstore" / channel / "library" / "apps" / "demo" / "latest.zip").exists()
    versions_path = output / "appstore" / channel / "apps-verson.json"
    if channel == "dev":
        assert json.loads(versions_path.read_text()) == [{"id": "demo", "version": "1.0"}]
    else:
        assert not versions_path.exists()


def test_dictionary_only_change_updates_dataset_without_changing_app_hash(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    baseline, old_version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")
    path = build_fixture / "metadata" / "database-types.json"
    definitions = json.loads(path.read_text())
    definitions["postgresql"]["port"] = 5433
    path.write_text(json.dumps(definitions))
    current, new_version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")
    assert old_version != new_version
    assert baseline["apps"] == current["apps"]
    assert baseline["metadata"] != current["metadata"]


@pytest.mark.parametrize("schema_version", ["1", "2"])
def test_dictionary_only_increment_delivers_shared_file_without_rebuilding_apps(build_fixture, monkeypatch, schema_version):
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(library_publish, "apps_in_ref", lambda ref: {"demo"})
    monkeypatch.setattr(library_publish, "changed_apps_since", lambda ref: set())
    monkeypatch.setattr(library_publish, "build_app_updated_at_map", lambda: {})
    previous, previous_version = library_publish.build_apps_index_with_version("dev", "2026-01-01T00:00:00Z")
    previous["schemaVersion"] = schema_version
    dictionary = build_fixture / "metadata" / "database-types.json"
    definitions = json.loads(dictionary.read_text())
    definitions["postgresql"]["port"] = 5433
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
    entry = manifest["metadata"]["databaseTypes"]
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
