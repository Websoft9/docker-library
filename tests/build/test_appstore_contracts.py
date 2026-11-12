from __future__ import annotations

import json
from zipfile import ZipFile

import pytest

from _helpers import load_build_module, REPO_ROOT


publish = load_build_module("appstore_contract_test", REPO_ROOT / "ci/scripts/library_publish.py")


@pytest.mark.parametrize("value", [
    {}, [], {"schemaVersion": "2", "catalog": {}, "library": {}},
    {"schemaVersion": 2, "catalog": {"schemaVersion": "1"}, "library": {"schemaVersion": "2"}},
    {"schemaVersion": "2", "catalog": {"schemaVersion": "0"}, "library": {"schemaVersion": "2"}},
])
def test_invalid_contract_config_fails_explicitly(build_fixture, monkeypatch, value):
    monkeypatch.setattr(publish, "ROOT", build_fixture)
    (build_fixture / publish.CONTRACT_PATH).write_text(json.dumps(value))
    with pytest.raises(SystemExit, match="invalid Appstore contract configuration"):
        publish.load_contracts()


def test_missing_contract_config_fails(build_fixture, monkeypatch):
    monkeypatch.setattr(publish, "ROOT", build_fixture)
    (build_fixture / publish.CONTRACT_PATH).unlink()
    with pytest.raises(SystemExit, match="invalid Appstore contract configuration"):
        publish.load_contracts()


def build_artifacts(build_fixture, monkeypatch, previous=None):
    monkeypatch.setattr(publish, "ROOT", build_fixture)
    monkeypatch.setattr(publish, "APPS_DIR", build_fixture / "apps")
    monkeypatch.setattr(publish, "build_app_updated_at_map", lambda: {})
    monkeypatch.setattr(publish, "changed_apps_since", lambda ref: set())
    catalog = build_fixture / "catalog"
    catalog.mkdir(exist_ok=True)
    for filename in publish.CATALOG_FILE_NAMES:
        (catalog / filename).write_text("[]\n")
    output = build_fixture / "output"
    publish.build_v2_appstore_artifacts(
        output, catalog, "library-dev.zip", {"Version": "dev-test", "schemaVersion": publish.library_schema_version()},
        "unused", None, "unused", "dev", "2026-01-01T00:00:00Z",
        previous_apps_index=previous,
    )
    return output


@pytest.mark.parametrize("component", ["root", "catalog", "library"])
def test_configured_versions_propagate_to_all_artifacts(build_fixture, monkeypatch, component):
    config = build_fixture / publish.CONTRACT_PATH
    expected = json.loads(config.read_text())
    entry = expected if component == "root" else expected[component]
    entry["schemaVersion"] = str(int(entry["schemaVersion"]) + 1)
    config.write_text(json.dumps(expected))
    output = build_artifacts(build_fixture, monkeypatch)
    root = json.loads((output / "manifests/appstore-manifest.json").read_text())
    assert root["schemaVersion"] == expected["schemaVersion"]
    for name in ("catalog", "library"):
        manifest = json.loads((output / name / "manifest.json").read_text())
        assert root[name]["schemaVersion"] == expected[name]["schemaVersion"]
        assert manifest["schemaVersion"] == expected[name]["schemaVersion"]
        if name == "library":
            for key in ("appsIndex", "appsDelta"):
                artifact = json.loads((output / name / manifest[key]).read_text())
                assert artifact["schemaVersion"] == expected[name]["schemaVersion"]
            with ZipFile(output / name / manifest["fullPackage"]) as archive:
                metadata = json.loads(archive.read("library/library.json"))
                assert metadata["schemaVersion"] == expected[name]["schemaVersion"]


@pytest.mark.parametrize("old_schema,new_schema", [("1", "2"), ("2", "3"), ("3", "4")])
def test_historical_contract_forces_full_seed(build_fixture, monkeypatch, old_schema, new_schema):
    monkeypatch.setattr(publish, "ROOT", build_fixture)
    monkeypatch.setattr(publish, "APPS_DIR", build_fixture / "apps")
    previous, _ = publish.build_apps_index_with_version("dev", "before")
    previous["schemaVersion"] = old_schema
    config = build_fixture / publish.CONTRACT_PATH
    contracts = publish.load_contracts()
    contracts["library"]["schemaVersion"] = new_schema
    config.write_text(json.dumps(contracts))
    baseline = build_fixture / "baseline.json"
    baseline.write_text(json.dumps(previous))
    previous = publish.load_previous_apps_index(str(baseline), "dev")
    output = build_artifacts(build_fixture, monkeypatch, previous)
    manifest = json.loads((output / "library/manifest.json").read_text())
    assert manifest["schemaVersion"] == new_schema
    assert manifest["supportsPartialUpdate"] is False
    assert (output / "library/apps/demo/latest.zip").is_file()
    delta = json.loads((output / "library" / manifest["appsDelta"]).read_text())
    assert delta["fromVersion"] == "initial"


@pytest.mark.parametrize("component", ["catalog", "library"])
@pytest.mark.parametrize("field", ["schemaVersion", "datasetVersion"])
def test_component_mismatch_is_rejected(build_fixture, monkeypatch, component, field):
    output = build_artifacts(build_fixture, monkeypatch)
    path = output / component / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest[field] = "unexpected"
    path.write_text(json.dumps(manifest))
    with pytest.raises(SystemExit, match="mismatched Appstore component"):
        publish.validate_appstore_artifacts(output)


@pytest.mark.parametrize("manifest", ["catalog/manifest.json", "library/manifest.json", "manifests/appstore-manifest.json"])
def test_build_validation_requires_manifest_checksums(build_fixture, monkeypatch, manifest):
    output = build_artifacts(build_fixture, monkeypatch)
    path = output / manifest
    path.with_name(f"{path.name}.sha256").unlink()
    with pytest.raises(SystemExit, match="missing appstore manifest checksum"):
        publish.validate_appstore_artifacts(output)


def test_contract_only_change_updates_combination_identity(build_fixture, monkeypatch):
    output = build_artifacts(build_fixture, monkeypatch)
    path = output / "manifests/appstore-manifest.json"
    before = json.loads(path.read_text())
    config = build_fixture / publish.CONTRACT_PATH
    contracts = publish.load_contracts()
    contracts["catalog"]["schemaVersion"] = str(int(contracts["catalog"]["schemaVersion"]) + 1)
    config.write_text(json.dumps(contracts))
    build_artifacts(build_fixture, monkeypatch)
    after = json.loads(path.read_text())
    assert before["datasetVersion"] != after["datasetVersion"]
    assert before["catalog"]["datasetVersion"] == after["catalog"]["datasetVersion"]
