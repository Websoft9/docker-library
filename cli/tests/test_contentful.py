from __future__ import annotations

import json
from pathlib import Path
import sys
import types

import pytest
from typer.testing import CliRunner

from libs import contentful, main


runner = CliRunner()


def write_catalog_schema(repo_fixture):
    source = Path(__file__).resolve().parents[2] / "metadata" / "catalog.schema.json"
    target = repo_fixture / "metadata" / "catalog.schema.json"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def write_catalog_draft(repo_fixture, payload):
    write_catalog_schema(repo_fixture)
    catalog_dir = repo_fixture / "metadata" / ".catalog"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    (catalog_dir / "demo.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")


def make_args(**overrides):
    defaults = {
        "app": "demo",
        "environment": "master",
        "drafts_dir": "metadata/.catalog",
        "apply": False,
        "update_machine": False,
    }
    defaults.update(overrides)
    return types.SimpleNamespace(**defaults)


def test_build_machine_fields_from_variables():
    variables = {
        "name": "demo",
        "trademark": "Demo",
        "release": True,
        "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
        "requirements": {"cpu": "2", "memory": "4", "disk": "20"},
    }

    fields = contentful.build_machine_fields(variables)

    assert fields == {
        "key": "demo",
        "title": "Demo",
        "distribution": [{"key": "community", "value": ["1.0", "latest"]}],
        "vcpu": 2,
        "memory": 4,
        "storage": 20,
        "app_store": True,
        "production": True,
    }


def test_build_machine_fields_title_falls_back_to_name():
    fields = contentful.build_machine_fields({"name": "demo"})

    assert fields["title"] == "demo"


@pytest.mark.parametrize(("memory", "expected"), [("1.5", 2), (1.5, 2), ("2.0", 2), (2, 2)])
def test_build_machine_fields_rounds_fractional_memory_up(memory, expected):
    variables = {"name": "youtrack", "requirements": {"memory": memory}}

    fields = contentful.build_machine_fields(variables)

    assert fields["memory"] == expected
    assert isinstance(fields["memory"], int)
    assert variables["requirements"]["memory"] == memory


@pytest.mark.parametrize("memory", ["invalid", "NaN", "Infinity", 0, -1, True])
def test_build_machine_fields_rejects_invalid_memory_with_app_context(memory):
    with pytest.raises(ValueError, match=r"demo: requirements\.memory must be a positive, finite number"):
        contentful.build_machine_fields({"name": "demo", "requirements": {"memory": memory}})


def test_build_machine_fields_hides_archived_and_internal_apps():
    variables = {"name": "demo", "release": True}

    archived = contentful.build_machine_fields(variables, active=False)
    internal = contentful.build_machine_fields({**variables, "scope": "internal"})

    assert archived["app_store"] is False
    assert archived["production"] is False
    assert internal["app_store"] is False
    assert internal["production"] is False


def test_build_machine_fields_allows_dev_only_public_app():
    fields = contentful.build_machine_fields({"name": "demo", "release": False})

    assert fields["app_store"] is True
    assert fields["production"] is False


def test_build_draft_fields_filters_empty_values():
    assert contentful.build_draft_fields({}) == {}
    assert contentful.build_draft_fields({"trademark": "Demo", "summary": None, "screenshots": []}) == {
        "trademark": "Demo",
        "screenshots": [],
    }


def test_localized_wraps_values_with_en_us():
    assert contentful.localized({"key": "demo"}) == {"key": {"en-US": "demo"}}


def test_catalog_template_keys_match_script_contract():
    from pathlib import Path

    template_path = Path(__file__).resolve().parents[2] / "metadata" / "templates" / "catalog.json"
    template = json.loads(template_path.read_text(encoding="utf-8"))

    assert set(template) == set(contentful.DRAFT_FIELD_KEYS) | {"catalogBindings"}


def test_sync_app_dry_run_preview(repo_fixture, app_factory):
    app_factory("demo", variables={
        "name": "demo",
        "trademark": "Demo",
        "release": False,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
    })

    payload = contentful.sync_app("demo", "master", "metadata/.catalog", apply=False, update_machine=False)

    assert payload["action"] == "create"
    assert payload["dry_run"] is True
    assert payload["exists_unknown"] is True
    assert "note" in payload
    assert payload["machine_fields"]["key"] == "demo"
    assert payload["machine_fields"]["production"] is False


def test_sync_app_dry_run_probes_existing_entry(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    fake_client = FakeClient(existing=FakeEntry())
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.sync_app("demo", "master", "metadata/.catalog", apply=False, update_machine=False)

    assert payload["action"] == "update-machine"
    assert payload["dry_run"] is True
    assert payload["exists"] is True


def test_sync_app_dry_run_probes_missing_entry(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    fake_client = FakeClient()
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.sync_app("demo", "master", "metadata/.catalog", apply=False, update_machine=False)

    assert payload["action"] == "create"
    assert payload["dry_run"] is True
    assert payload["exists"] is False


def test_contentful_create_cli_preview_exit_0(repo_fixture, app_factory):
    app_factory("demo", variables={
        "name": "demo",
        "trademark": "Demo",
        "release": False,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
    })

    result = runner.invoke(main.app, ["catalog-push", "--app", "demo", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["action"] == "create"
    assert payload["dry_run"] is True


def test_contentful_create_cli_missing_app_exit_4(repo_fixture):
    result = runner.invoke(main.app, ["catalog-push", "--app", "missing", "--json"])

    assert result.exit_code == 4


def test_sync_app_apply_requires_token(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    monkeypatch.delenv("CONTENTFUL_ACCESS_TOKEN", raising=False)

    with __import__("pytest").raises(FileNotFoundError, match="CONTENTFUL_ACCESS_TOKEN"):
        contentful.sync_app("demo", "master", "metadata/.catalog", apply=True, update_machine=False)


def test_sync_app_apply_accepts_explicit_token(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    monkeypatch.delenv("CONTENTFUL_ACCESS_TOKEN", raising=False)
    captured = {}

    def fake_client_factory(token):
        captured["token"] = token
        return FakeClient()

    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=fake_client_factory))

    payload = contentful.sync_app(
        "demo", "master", "metadata/.catalog", apply=True, update_machine=False, token="explicit-token"
    )

    assert payload["action"] == "created"
    assert captured["token"] == "explicit-token"


def test_sync_app_apply_uses_default_contentful_env_file(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "contentful.env").write_text(
        "CONTENTFUL_ACCESS_TOKEN=file-token\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("CONTENTFUL_ACCESS_TOKEN", raising=False)
    captured = {}

    def fake_client_factory(token):
        captured["token"] = token
        return FakeClient()

    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=fake_client_factory))

    payload = contentful.sync_app("demo", "master", "metadata/.catalog", apply=True, update_machine=False)

    assert payload["action"] == "created"
    assert captured["token"] == "file-token"


def test_contentful_create_cli_forwards_token(repo_fixture, app_factory, monkeypatch):
    calls = {}

    def fake_sync_app(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "action": "create", "dry_run": True}

    monkeypatch.setattr(contentful, "sync_app", fake_sync_app)

    result = runner.invoke(main.app, ["catalog-push", "--app", "demo", "--token", "abc", "--json"])

    assert result.exit_code == 0
    assert calls["token"] == "abc"


def test_contentful_create_cli_forwards_env_file(repo_fixture, app_factory, monkeypatch):
    calls = {}

    def fake_sync_app(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "action": "create", "dry_run": True}

    monkeypatch.setattr(contentful, "sync_app", fake_sync_app)

    result = runner.invoke(
        main.app,
        ["catalog-push", "--app", "demo", "--env-file", ".secrets/contentful.env", "--json"],
    )

    assert result.exit_code == 0
    assert calls["env_file"] == ".secrets/contentful.env"


def test_contentful_create_cli_accepts_catalog_dir(repo_fixture, app_factory, monkeypatch):
    calls = {}

    def fake_sync_app(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "action": "create", "dry_run": True}

    monkeypatch.setattr(contentful, "sync_app", fake_sync_app)

    result = runner.invoke(
        main.app,
        ["catalog-push", "--app", "demo", "--catalog-dir", "metadata/.catalog", "--json"],
    )

    assert result.exit_code == 0
    assert calls["drafts_dir"] == "metadata/.catalog"


def test_catalog_push_cli_forwards_catalog_dir(repo_fixture, app_factory, monkeypatch):
    calls = {}

    def fake_sync_app(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "action": "create", "dry_run": True}

    monkeypatch.setattr(contentful, "sync_app", fake_sync_app)

    result = runner.invoke(
        main.app,
        ["catalog-push", "--app", "demo", "--catalog-dir", "metadata/.catalog", "--json"],
    )

    assert result.exit_code == 0
    assert calls["drafts_dir"] == "metadata/.catalog"


def test_update_fields_dry_run_preview(repo_fixture, app_factory):
    payload = contentful.update_fields("demo", "master", {"appStore": False, "production": False}, apply=False)
    assert payload["action"] == "update"
    assert payload["dry_run"] is True
    assert payload["fields"] == {"app_store": False, "production": False}


def test_update_fields_apply_updates_existing_entry(repo_fixture, app_factory, monkeypatch):
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    entry = FakeEntry()
    fake_client = FakeClient(existing=entry)
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.update_fields("demo", "master", {"appStore": False, "production": False}, apply=True)

    assert payload["action"] == "updated"
    assert payload["dry_run"] is False
    assert entry.fields_data["app_store"] is False
    assert entry.fields_data["production"] is False


def test_update_fields_apply_not_found(repo_fixture, app_factory, monkeypatch):
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    fake_client = FakeClient()
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.update_fields("demo", "master", {"appStore": False}, apply=True)

    assert payload["action"] == "not-found"
    assert payload["dry_run"] is False


def test_contentful_update_cli_preview_exit_0(repo_fixture, app_factory):
    result = runner.invoke(
        main.app,
        ["catalog-update", "--app", "demo", "--fields", '{"appStore": false, "production": false}', "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["action"] == "update"
    assert payload["dry_run"] is True


def test_contentful_update_cli_invalid_fields_exit_2(repo_fixture, app_factory):
    result = runner.invoke(main.app, ["catalog-update", "--app", "demo", "--fields", "not-json", "--json"])

    assert result.exit_code == 2


def test_contentful_update_cli_forwards_fields_and_apply(repo_fixture, app_factory, monkeypatch):
    calls = {}

    def fake_update_fields(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "action": "updated", "dry_run": False}

    monkeypatch.setattr(contentful, "update_fields", fake_update_fields)

    result = runner.invoke(
        main.app,
        ["catalog-update", "--app", "demo", "--fields", '{"appStore": false}', "--apply", "--json"],
    )

    assert result.exit_code == 0
    assert calls["fields"] == {"appStore": False}
    assert calls["apply"] is True


class FakeEntry:
    def __init__(self, entry_id: str | None = None):
        self.fields_data = {}
        self.sys = {"id": entry_id} if entry_id else {}

    def fields(self, locale):
        return self.fields_data

    def save(self):
        pass

    def publish(self):
        pass


class FakeEntries:
    def __init__(self, existing=None, catalogs=None):
        self.existing = existing
        self.created = None
        self.catalogs = catalogs or {}

    def all(self, query):
        if query.get("content_type") == "catalog":
            key = query.get("fields.key")
            return [self.catalogs[key]] if key in self.catalogs else []
        return [self.existing] if self.existing else []

    def create(self, resource_id=None, attributes=None):
        assert resource_id is None
        assert attributes is not None
        assert "content_type_id" in attributes
        assert "fields" in attributes
        self.created = (resource_id, attributes)
        return FakeEntry()


class FakeClient:
    def __init__(self, existing=None, catalogs=None):
        self.entries_map = {"master": FakeEntries(existing, catalogs)}

    def entries(self, space_id, environment):
        return self.entries_map[environment]


def test_sync_app_apply_creates_entry_when_absent(repo_fixture, app_factory, monkeypatch):
    app_factory("demo", variables={
        "name": "demo",
        "trademark": "Demo",
        "release": False,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
    })
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    fake_client = FakeClient()
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.sync_app("demo", "master", "metadata/.catalog", apply=True, update_machine=False)

    entries = fake_client.entries_map["master"]
    assert payload["action"] == "created"
    assert entries.created[0] is None
    assert entries.created[1]["content_type_id"] == "product"
    assert entries.created[1]["fields"]["key"]["en-US"] == "demo"
    assert entries.created[1]["fields"]["title"]["en-US"] == "Demo"
    assert entries.created[1]["fields"]["app_store"]["en-US"] is True
    assert entries.created[1]["fields"]["production"]["en-US"] is False


def test_sync_app_apply_creates_archived_entry_hidden(repo_fixture, app_factory, monkeypatch):
    app_factory("demo", archived=True, variables={
        "name": "demo",
        "trademark": "Demo",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
    })
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    fake_client = FakeClient()
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    contentful.sync_app("demo", "master", "metadata/.catalog", apply=True, update_machine=False)

    fields = fake_client.entries_map["master"].created[1]["fields"]
    assert fields["app_store"]["en-US"] is False
    assert fields["production"]["en-US"] is False


def test_sync_app_apply_creates_entry_with_catalog_links(repo_fixture, app_factory, monkeypatch):
    app_factory(
        "demo",
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": False,
            "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
            "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
        },
    )
    metadata_dir = repo_fixture / "metadata"
    write_catalog_schema(repo_fixture)
    (repo_fixture / "metadata" / ".catalog").mkdir(parents=True, exist_ok=True)
    (repo_fixture / "metadata" / ".catalog" / "demo.json").write_text(
        json.dumps(
            {
                "trademark": "Demo",
                "catalogBindings": [{"parentKey": "collaboration", "childKey": "document"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (metadata_dir / "catalog-taxonomy.json").write_text(
        json.dumps(
            {
                "version": 1,
                "source": "https://example.com/catalog_en.json",
                "locale": "en",
                "categories": [
                    {
                        "key": "collaboration",
                        "title": "Collaboration & Office",
                        "position": 7,
                        "children": [{"key": "document", "title": "Document Collaboration", "position": 1}],
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    fake_client = FakeClient(catalogs={"document": FakeEntry("doc-entry-id")})
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.sync_app("demo", "master", "metadata/.catalog", apply=True, update_machine=False)

    entries = fake_client.entries_map["master"]
    assert payload["action"] == "created"
    assert payload["catalog_bindings"] == [{"parentKey": "collaboration", "childKey": "document"}]
    assert entries.created[1]["fields"]["catalog"]["en-US"] == [
        {"sys": {"type": "Link", "linkType": "Entry", "id": "doc-entry-id"}}
    ]


def test_sync_app_preview_validates_catalog_bindings_against_taxonomy(repo_fixture, app_factory):
    app_factory("demo")
    metadata_dir = repo_fixture / "metadata"
    write_catalog_schema(repo_fixture)
    (repo_fixture / "metadata" / ".catalog").mkdir(parents=True, exist_ok=True)
    (repo_fixture / "metadata" / ".catalog" / "demo.json").write_text(
        json.dumps(
            {
                "trademark": "Demo",
                "catalogBindings": [{"parentKey": "collaboration", "childKey": "missing-child"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (metadata_dir / "catalog-taxonomy.json").write_text(
        json.dumps(
            {
                "version": 1,
                "source": "https://example.com/catalog_en.json",
                "locale": "en",
                "categories": [
                    {
                        "key": "collaboration",
                        "title": "Collaboration & Office",
                        "position": 7,
                        "children": [{"key": "document", "title": "Document Collaboration", "position": 1}],
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with __import__("pytest").raises(ValueError, match="invalid catalogBindings"):
        contentful.sync_app("demo", "master", "metadata/.catalog", apply=False, update_machine=False)


def test_sync_app_apply_refreshes_machine_fields_only(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    write_catalog_draft(repo_fixture, {"trademark": "Demo", "summary": "Seed summary"})
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    existing = FakeEntry()
    existing.fields_data["summary"] = "Edited in Contentful"
    existing.fields_data["key"] = "demo"
    fake_client = FakeClient(existing=existing)
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.sync_app("demo", "master", "metadata/.catalog", apply=True, update_machine=False)

    assert payload["action"] == "update-machine"
    assert fake_client.entries_map["master"].created is None
    assert existing.fields_data["summary"] == "Edited in Contentful"
    assert existing.fields_data["key"] == "demo"
    assert existing.fields_data["title"] == "Demo"


def test_sync_app_apply_overwrite_rewrites_content(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    write_catalog_draft(repo_fixture, {"trademark": "Demo", "summary": "Seed summary"})
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    existing = FakeEntry()
    existing.fields_data["summary"] = "Edited in Contentful"
    fake_client = FakeClient(existing=existing)
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.sync_app(
        "demo", "master", "metadata/.catalog", apply=True, update_machine=False, overwrite=True
    )

    assert payload["action"] == "updated"
    assert existing.fields_data["summary"] == "Seed summary"


def test_sync_app_rejects_overwrite_with_update_machine(repo_fixture, app_factory):
    app_factory("demo")

    with __import__("pytest").raises(ValueError, match="cannot be combined"):
        contentful.sync_app(
            "demo", "master", "metadata/.catalog", apply=True, update_machine=True, overwrite=True
        )


def test_catalog_push_cli_forwards_overwrite(repo_fixture, app_factory, monkeypatch):
    calls = {}

    def fake_sync_app(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "action": "updated", "dry_run": False}

    monkeypatch.setattr(contentful, "sync_app", fake_sync_app)

    result = runner.invoke(main.app, ["catalog-push", "--app", "demo", "--apply", "--overwrite", "--json"])

    assert result.exit_code == 0
    assert calls["overwrite"] is True
    assert calls["apply"] is True
