from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from libs import catalog, main


runner = CliRunner()


def write_catalog_schema(repo_fixture):
    source = Path(__file__).resolve().parents[2] / "metadata" / "catalog.schema.json"
    target = repo_fixture / "metadata" / "catalog.schema.json"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def sample_catalog():
    return [
        {
            "key": "collaboration",
            "title": "Collaboration & Office",
            "position": 7,
            "linkedFrom": {
                "catalogCollection": {
                    "items": [
                        {"key": "document", "title": "Document Collaboration", "position": None},
                        {"key": "pm-task", "title": "Project and Task", "position": 1},
                    ]
                }
            },
        }
    ]


def sample_product(app_key: str = "affine"):
    return [
        {
            "key": app_key,
            "trademark": "AFFiNE",
            "summary": "Summary",
            "overview": "Overview",
            "description": "Description",
            "websiteurl": "https://affine.pro",
            "screenshots": [
                {"id": "shot-1", "key": "main", "value": "https://example.com/shot.png"}
            ],
            "distribution": [{"key": "community", "value": ["0.27.4", "latest"]}],
            "vcpu": 2,
            "memory": 4,
            "storage": 8,
            "logo": {"imageurl": "https://example.com/logo.png"},
            "catalogCollection": {
                "items": [
                    {
                        "key": "document",
                        "title": "Document Collaboration",
                        "catalogCollection": {"items": [{"key": "collaboration", "title": "Collaboration & Office", "position": 7}]},
                    }
                ]
            },
        }
    ]


def test_normalize_catalog_keeps_parent_and_children():
    payload = catalog.normalize_catalog(sample_catalog(), "https://example.com/catalog_en.json")

    assert payload["version"] == 1
    assert payload["source"] == "https://example.com/catalog_en.json"
    assert payload["locale"] == "en"
    assert payload["categories"] == [
        {
            "key": "collaboration",
            "title": "Collaboration & Office",
            "position": 7,
            "children": [
                {"key": "document", "title": "Document Collaboration", "position": None},
                {"key": "pm-task", "title": "Project and Task", "position": 1},
            ],
        }
    ]


def test_refresh_catalog_preview(monkeypatch):
    monkeypatch.setattr(catalog.http, "get", lambda url: DummyResponse(sample_catalog()))

    payload = catalog.refresh_catalog(url="https://example.com/catalog_en.json", apply=False)

    assert payload["action"] == "preview"
    assert payload["dry_run"] is True
    assert payload["category_count"] == 1
    assert payload["snapshot"]["categories"][0]["key"] == "collaboration"


def test_refresh_catalog_apply_writes_snapshot(repo_fixture, monkeypatch):
    monkeypatch.setattr(catalog.http, "get", lambda url: DummyResponse(sample_catalog()))

    payload = catalog.refresh_catalog(
        url="https://example.com/catalog_en.json",
        output="metadata/catalog-taxonomy.json",
        apply=True,
    )

    assert payload["action"] == "written"
    target = repo_fixture / "metadata" / "catalog-taxonomy.json"
    assert json.loads(target.read_text(encoding="utf-8"))["categories"][0]["key"] == "collaboration"


def test_refresh_catalog_can_check_product_schema(monkeypatch):
    responses = {
        "https://example.com/catalog_en.json": DummyResponse(sample_catalog()),
        "https://example.com/product_en.json": DummyResponse(sample_product()),
    }
    monkeypatch.setattr(catalog.http, "get", lambda url: responses[url])

    payload = catalog.refresh_catalog(
        url="https://example.com/catalog_en.json",
        product_url="https://example.com/product_en.json",
        check_product_schema=True,
        apply=False,
    )

    assert payload["product_check"]["entry_count"] == 1
    assert "catalogCollection" in payload["product_check"]["sample_fields"]
    assert payload["product_check"]["schema_valid"] is True


def test_refresh_catalog_rejects_invalid_product_schema(monkeypatch):
    responses = {
        "https://example.com/catalog_en.json": DummyResponse(sample_catalog()),
        "https://example.com/product_en.json": DummyResponse([{"key": "demo"}]),
    }
    monkeypatch.setattr(catalog.http, "get", lambda url: responses[url])

    import pytest

    with pytest.raises(ValueError, match="invalid published product artifact"):
        catalog.refresh_catalog(
            url="https://example.com/catalog_en.json",
            product_url="https://example.com/product_en.json",
            check_product_schema=True,
            apply=False,
        )


def test_pull_catalog_preview_extracts_repo_fields(monkeypatch):
    monkeypatch.setattr(catalog.http, "get", lambda url: DummyResponse(sample_product("demo")))

    payload = catalog.pull_catalog(app_name="demo", product_url="https://example.com/product_en.json", apply=False)

    assert payload["action"] == "preview"
    assert payload["incoming"]["trademark"] == "AFFiNE"
    assert payload["incoming"]["screenshots"] == ["https://example.com/shot.png"]
    assert payload["incoming"]["catalogBindings"] == [{"parentKey": "collaboration", "childKey": "document"}]


def test_pull_catalog_only_diff(monkeypatch):
    monkeypatch.setattr(catalog.http, "get", lambda url: DummyResponse(sample_product("demo")))

    payload = catalog.pull_catalog(app_name="demo", product_url="https://example.com/product_en.json", only_diff=True)

    assert payload["action"] == "diff"
    assert "incoming" not in payload


def test_pull_catalog_apply_writes_repo_catalog(repo_fixture, monkeypatch):
    write_catalog_schema(repo_fixture)
    monkeypatch.setattr(catalog.http, "get", lambda url: DummyResponse(sample_product("demo")))

    payload = catalog.pull_catalog(app_name="demo", product_url="https://example.com/product_en.json", apply=True)

    assert payload["action"] == "written"
    target = repo_fixture / "metadata" / "catalog" / "demo.json"
    written = json.loads(target.read_text(encoding="utf-8"))
    assert written["catalogBindings"] == [{"parentKey": "collaboration", "childKey": "document"}]


def test_catalog_refresh_cli_contract(monkeypatch):
    monkeypatch.setattr(
        catalog,
        "refresh_catalog",
        lambda **kwargs: {"action": "preview", "dry_run": True, "source": kwargs["url"], "output": kwargs["output"]},
    )

    result = runner.invoke(main.app, ["catalog-refresh", "--url", "https://example.com/catalog_en.json", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["action"] == "preview"
    assert payload["source"] == "https://example.com/catalog_en.json"


def test_catalog_refresh_cli_forwards_product_check(monkeypatch):
    calls = {}

    def fake_refresh_catalog(**kwargs):
        calls.update(kwargs)
        return {"action": "preview", "dry_run": True}

    monkeypatch.setattr(catalog, "refresh_catalog", fake_refresh_catalog)

    result = runner.invoke(
        main.app,
        ["catalog-refresh", "--check-product-schema", "--product-url", "https://example.com/product_en.json", "--json"],
    )

    assert result.exit_code == 0
    assert calls["check_product_schema"] is True
    assert calls["product_url"] == "https://example.com/product_en.json"


def test_catalog_pull_cli_contract(monkeypatch):
    calls = {}

    def fake_pull_catalog(**kwargs):
        calls.update(kwargs)
        return {"action": "diff", "dry_run": True, "app": kwargs["app_name"]}

    monkeypatch.setattr(catalog, "pull_catalog", fake_pull_catalog)

    result = runner.invoke(main.app, ["catalog-pull", "--app", "demo", "--only-diff", "--json"])

    assert result.exit_code == 0
    assert calls["only_diff"] is True
    assert json.loads(result.stdout)["app"] == "demo"
