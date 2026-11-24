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

    payload = catalog.pull_catalog(
        app_name="demo", source="artifact", product_url="https://example.com/product_en.json", apply=False
    )

    assert payload["action"] == "preview"
    assert payload["source_kind"] == "artifact"
    assert payload["incoming"]["trademark"] == "AFFiNE"
    assert payload["incoming"]["screenshots"] == ["https://example.com/shot.png"]
    assert payload["incoming"]["catalogBindings"] == [{"parentKey": "collaboration", "childKey": "document"}]


def test_pull_catalog_only_diff(monkeypatch):
    monkeypatch.setattr(catalog.http, "get", lambda url: DummyResponse(sample_product("demo")))

    payload = catalog.pull_catalog(
        app_name="demo", source="artifact", product_url="https://example.com/product_en.json", only_diff=True
    )

    assert payload["action"] == "diff"
    assert "incoming" not in payload


def test_pull_catalog_apply_writes_working_copy(repo_fixture, monkeypatch):
    write_catalog_schema(repo_fixture)
    monkeypatch.setattr(catalog.http, "get", lambda url: DummyResponse(sample_product("demo")))

    payload = catalog.pull_catalog(
        app_name="demo", source="artifact", product_url="https://example.com/product_en.json", apply=True
    )

    assert payload["action"] == "written"
    target = repo_fixture / "metadata" / ".catalog" / "demo.json"
    written = json.loads(target.read_text(encoding="utf-8"))
    assert written["catalogBindings"] == [{"parentKey": "collaboration", "childKey": "document"}]


def test_pull_catalog_apply_accepts_absolute_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(catalog, "fetch_product_entry", lambda *args, **kwargs: sample_product("demo")[0])

    payload = catalog.pull_catalog(app_name="demo", catalog_dir=str(tmp_path), apply=True)

    assert payload["action"] == "written"
    assert payload["catalog_path"] == str(tmp_path / "demo.json")
    assert (tmp_path / "demo.json").exists()


def test_pull_catalog_defaults_to_live_contentful(monkeypatch):
    entry = {
        "key": "demo",
        "trademark": "AFFiNE",
        "summary": "Live summary",
        "catalogCollection": {
            "items": [
                {
                    "key": "document",
                    "catalogCollection": {"items": [{"key": "collaboration", "title": "Collab", "position": 7}]},
                }
            ]
        },
    }
    monkeypatch.setattr(catalog, "fetch_product_entry", lambda *args, **kwargs: entry)

    payload = catalog.pull_catalog(app_name="demo", only_diff=True)

    assert payload["source_kind"] == "contentful"
    assert payload["source"].startswith(catalog.CONTENTFUL_GRAPHQL_URL)


def test_fetch_product_entry_requires_graphql_token(monkeypatch):
    monkeypatch.setattr(catalog, "resolve_secret", lambda *args, **kwargs: None)

    try:
        catalog.fetch_product_entry("demo")
    except FileNotFoundError as error:
        assert "CONTENTFUL_GRAPHQL_TOKEN" in str(error)
    else:
        raise AssertionError("expected FileNotFoundError for missing GraphQL token")


def test_fetch_product_entry_reports_rejected_token(monkeypatch):
    import requests as requests_module

    class Rejected:
        status_code = 401

        def raise_for_status(self):
            raise requests_module.HTTPError("401 Client Error", response=self)

    monkeypatch.setattr(catalog.http, "post_with_retries", lambda *args, **kwargs: Rejected())
    monkeypatch.setattr(catalog, "resolve_secret", lambda *args, **kwargs: "bad-token")

    try:
        catalog.fetch_product_entry("demo")
    except ValueError as error:
        assert "Content Delivery/GraphQL API token" in str(error)
    else:
        raise AssertionError("expected ValueError for a rejected token")


def test_fetch_product_entry_posts_graphql(monkeypatch):
    captured = {}

    class GraphqlResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": {"productCollection": {"items": [{"key": "demo"}]}}}

    def fake_post(url, json_body=None, headers=None, timeout=None):
        captured.update(url=url, json_body=json_body, headers=headers, timeout=timeout)
        return GraphqlResponse()

    monkeypatch.setattr(catalog.http, "post_with_retries", fake_post)
    monkeypatch.setattr(catalog, "resolve_secret", lambda *args, **kwargs: "tok")

    entry = catalog.fetch_product_entry("demo", locale="zh-CN")

    assert entry["key"] == "demo"
    assert captured["url"] == catalog.CONTENTFUL_GRAPHQL_URL
    assert captured["json_body"]["variables"] == {"locale": "zh-CN", "key": "demo"}
    assert captured["headers"]["Authorization"] == "Bearer tok"
    assert captured["timeout"] == (5.0, 60.0)


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
    assert calls["source"] == "contentful"
    assert calls["locale"] == "en-US"
    assert json.loads(result.stdout)["app"] == "demo"


def test_catalog_pull_cli_forwards_artifact_source(monkeypatch):
    calls = {}

    def fake_pull_catalog(**kwargs):
        calls.update(kwargs)
        return {"action": "preview", "dry_run": True, "app": kwargs["app_name"]}

    monkeypatch.setattr(catalog, "pull_catalog", fake_pull_catalog)

    result = runner.invoke(
        main.app,
        ["catalog-pull", "--app", "demo", "--from", "artifact", "--locale", "zh-CN", "--json"],
    )

    assert result.exit_code == 0
    assert calls["source"] == "artifact"
    assert calls["locale"] == "zh-CN"
