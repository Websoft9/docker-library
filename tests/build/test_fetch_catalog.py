from __future__ import annotations

import json

from _helpers import REPO_ROOT, load_build_module

fetch_catalog = load_build_module("fetch_catalog_test", REPO_ROOT / "build" / "fetch_catalog.py")


def test_fetch_catalog_entries_returns_collection_items(monkeypatch):
    monkeypatch.setattr(
        fetch_catalog,
        "run_query",
        lambda token, query, variables: {
            "catalog": {"linkedFrom": {"catalogCollection": {"items": [{"key": "web", "title": "Web"}]}}}
        },
    )

    entries = fetch_catalog.fetch_catalog_entries("token", "en-US")

    assert entries == [{"key": "web", "title": "Web"}]


def test_fetch_product_entries_paginates_until_total(monkeypatch):
    calls = []

    def fake_run_query(token, query, variables):
        calls.append(variables["skip"])
        return {
            "productCollection": {
                "total": 120,
                "items": [{"sys": {"id": f"id-{variables['skip']}"}, "key": "demo"}],
            }
        }

    monkeypatch.setattr(fetch_catalog, "run_query", fake_run_query)

    items = fetch_catalog.fetch_product_entries("token", "en-US", True)

    assert calls == [0, 100]
    assert len(items) == 2


def test_write_json_writes_pretty_json(tmp_path):
    path = tmp_path / "catalog_en.json"

    fetch_catalog.write_json(path, [{"key": "web"}])

    assert json.loads(path.read_text(encoding="utf-8")) == [{"key": "web"}]


def test_main_requires_token(monkeypatch, tmp_path):
    import pytest

    monkeypatch.setattr("sys.argv", ["fetch_catalog.py", "--channel", "dev", "--output-dir", str(tmp_path)])
    monkeypatch.delenv("CONTENTFUL_GRAPHQL_TOKEN", raising=False)

    with pytest.raises(SystemExit, match="missing Contentful GraphQL token"):
        fetch_catalog.main()


def test_main_writes_all_catalog_outputs(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.argv", ["fetch_catalog.py", "--channel", "dev", "--output-dir", str(tmp_path), "--token", "token"])
    monkeypatch.setattr(fetch_catalog, "fetch_catalog_entries", lambda token, locale: [{"key": f"catalog-{locale}"}])
    monkeypatch.setattr(fetch_catalog, "fetch_product_entries", lambda token, locale, production: [{"key": f"product-{locale}", "production": production}])

    assert fetch_catalog.main() == 0
    assert json.loads((tmp_path / "catalog_en.json").read_text(encoding="utf-8")) == [{"key": "catalog-en-US"}]
    assert json.loads((tmp_path / "catalog_zh.json").read_text(encoding="utf-8")) == [{"key": "catalog-zh-CN"}]
    assert json.loads((tmp_path / "product_en.json").read_text(encoding="utf-8")) == [{"key": "product-en-US", "production": None}]
    assert json.loads((tmp_path / "product_zh.json").read_text(encoding="utf-8")) == [{"key": "product-zh-CN", "production": None}]
