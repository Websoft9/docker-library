from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from _helpers import REPO_ROOT, load_build_module

library_publish = load_build_module("library_publish_test", REPO_ROOT / "build" / "library_publish.py")


def test_hash_content_is_deterministic_and_input_sensitive():
    assert library_publish._hash_content("a", "b") == library_publish._hash_content("a", "b")
    assert library_publish._hash_content("a") != library_publish._hash_content("b")
    assert len(library_publish._hash_content("a")) == 16


def test_summarize_versions_deduplicates_and_preserves_order():
    editions = [
        {"dist": "community", "version": ["1.0", "1.0", "2.0"]},
        {"dist": "enterprise", "version": ["9.9"]},
    ]

    assert library_publish.summarize_versions(editions) == ["1.0", "2.0", "9.9"]


def test_app_package_and_checksum_entry_shapes():
    assert library_publish.build_app_package_entry("demo") == {"latest": "apps/demo/latest.zip"}
    assert library_publish.build_app_checksum_entry("demo") == {"latest": "apps/demo/latest.zip.sha256"}


def test_build_apps_index_with_fixture_apps(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)

    index = library_publish.build_apps_index("2026.01.01", "dev", "2026-01-01T00:00:00Z")

    assert index["schemaVersion"] == "1"
    assert index["appCount"] == 1
    entry = index["apps"][0]
    assert entry["app"] == "demo"
    assert entry["name"] == "demo"
    assert entry["trademark"] == "Demo App"
    assert entry["release"] is True
    assert entry["versions"] == ["1.0", "latest"]
    assert entry["path"] == "apps/demo"
    assert entry["package"] == {"latest": "apps/demo/latest.zip"}
    assert entry["checksum"] == {"latest": "apps/demo/latest.zip.sha256"}
    assert len(entry["hash"]) == 64


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
    assert library["supportsPartialUpdate"] is True
    assert library["appPackagesBase"] == "apps/"

    appstore = library_publish.build_appstore_manifest(
        "a-dsv", "dev", "2026-01-01T00:00:00Z", "c-dsv", "l-dsv"
    )
    assert appstore["catalog"]["manifest"] == "catalog/manifest.json"
    assert appstore["library"]["manifest"] == "library/manifest.json"


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


def test_load_library_json_defaults_version_when_missing(build_fixture, monkeypatch):
    monkeypatch.setattr(library_publish, "ROOT", build_fixture)
    (build_fixture / "library.json").write_text("{}\n", encoding="utf-8")

    payload = library_publish.load_library_json("2.0.0")

    assert payload == {"Version": "2.0.0"}


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
    monkeypatch.setattr(library_publish, "load_library_json", lambda version: {"Version": version})
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
