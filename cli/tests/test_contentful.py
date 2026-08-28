from __future__ import annotations

import json
import sys
import types

from typer.testing import CliRunner

from libs import contentful, main


runner = CliRunner()


def make_args(**overrides):
    defaults = {
        "app": "demo",
        "environment": "master",
        "drafts_dir": "metadata/contentful-drafts",
        "apply": False,
        "update_machine": False,
    }
    defaults.update(overrides)
    return types.SimpleNamespace(**defaults)


def test_build_machine_fields_from_variables():
    variables = {
        "name": "demo",
        "release": True,
        "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
        "requirements": {"cpu": "2", "memory": "4", "disk": "20"},
    }

    fields = contentful.build_machine_fields(variables)

    assert fields == {
        "key": "demo",
        "distribution": [{"key": "community", "value": ["1.0", "latest"]}],
        "vcpu": 2,
        "memory": 4,
        "storage": 20,
        "production": True,
    }


def test_build_draft_fields_filters_empty_values():
    assert contentful.build_draft_fields({}) == {}
    assert contentful.build_draft_fields({"trademark": "Demo", "summary": None, "screenshots": []}) == {
        "trademark": "Demo",
        "screenshots": [],
    }


def test_localized_wraps_values_with_en_us():
    assert contentful.localized({"key": "demo"}) == {"key": {"en-US": "demo"}}


def test_contentful_draft_template_keys_match_script_contract():
    from pathlib import Path

    template_path = Path(__file__).resolve().parents[2] / "metadata" / "templates" / "contentful-draft.json"
    template = json.loads(template_path.read_text(encoding="utf-8"))

    assert set(template) == set(contentful.DRAFT_FIELD_KEYS)


def test_sync_app_dry_run_preview(repo_fixture, app_factory):
    app_factory("demo", variables={
        "name": "demo",
        "trademark": "Demo",
        "release": False,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
    })

    payload = contentful.sync_app("demo", "master", "metadata/contentful-drafts", apply=False, update_machine=False)

    assert payload["action"] == "create"
    assert payload["dry_run"] is True
    assert payload["machine_fields"]["key"] == "demo"
    assert payload["machine_fields"]["production"] is False


def test_contentful_create_cli_preview_exit_0(repo_fixture, app_factory):
    app_factory("demo", variables={
        "name": "demo",
        "trademark": "Demo",
        "release": False,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
    })

    result = runner.invoke(main.app, ["contentful-create", "--app", "demo", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["action"] == "create"
    assert payload["dry_run"] is True


def test_contentful_create_cli_missing_app_exit_4(repo_fixture):
    result = runner.invoke(main.app, ["contentful-create", "--app", "missing", "--json"])

    assert result.exit_code == 4


def test_sync_app_apply_requires_token(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    monkeypatch.delenv("CONTENTFUL_ACCESS_TOKEN", raising=False)

    with __import__("pytest").raises(FileNotFoundError, match="CONTENTFUL_ACCESS_TOKEN"):
        contentful.sync_app("demo", "master", "metadata/contentful-drafts", apply=True, update_machine=False)


def test_sync_app_apply_accepts_explicit_token(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    monkeypatch.delenv("CONTENTFUL_ACCESS_TOKEN", raising=False)
    captured = {}

    def fake_client_factory(token):
        captured["token"] = token
        return FakeClient()

    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=fake_client_factory))

    payload = contentful.sync_app(
        "demo", "master", "metadata/contentful-drafts", apply=True, update_machine=False, token="explicit-token"
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

    payload = contentful.sync_app("demo", "master", "metadata/contentful-drafts", apply=True, update_machine=False)

    assert payload["action"] == "created"
    assert captured["token"] == "file-token"


def test_contentful_create_cli_forwards_token(repo_fixture, app_factory, monkeypatch):
    calls = {}

    def fake_sync_app(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "action": "create", "dry_run": True}

    monkeypatch.setattr(contentful, "sync_app", fake_sync_app)

    result = runner.invoke(main.app, ["contentful-create", "--app", "demo", "--token", "abc", "--json"])

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
        ["contentful-create", "--app", "demo", "--env-file", ".secrets/contentful.env", "--json"],
    )

    assert result.exit_code == 0
    assert calls["env_file"] == ".secrets/contentful.env"


def test_update_fields_dry_run_preview(repo_fixture, app_factory):
    payload = contentful.update_fields("demo", "master", {"appStore": False, "production": False}, apply=False)

    assert payload["action"] == "update"
    assert payload["dry_run"] is True
    assert payload["fields"] == {"appStore": False, "production": False}


def test_update_fields_apply_updates_existing_entry(repo_fixture, app_factory, monkeypatch):
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    entry = FakeEntry()
    fake_client = FakeClient(existing=entry)
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.update_fields("demo", "master", {"appStore": False, "production": False}, apply=True)

    assert payload["action"] == "updated"
    assert payload["dry_run"] is False
    assert entry.fields_data["appStore"] is False
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
        ["contentful-update", "--app", "demo", "--fields", '{"appStore": false, "production": false}', "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["action"] == "update"
    assert payload["dry_run"] is True


def test_contentful_update_cli_invalid_fields_exit_2(repo_fixture, app_factory):
    result = runner.invoke(main.app, ["contentful-update", "--app", "demo", "--fields", "not-json", "--json"])

    assert result.exit_code == 2


def test_contentful_update_cli_forwards_fields_and_apply(repo_fixture, app_factory, monkeypatch):
    calls = {}

    def fake_update_fields(**kwargs):
        calls.update(kwargs)
        return {"app": kwargs["app_name"], "action": "updated", "dry_run": False}

    monkeypatch.setattr(contentful, "update_fields", fake_update_fields)

    result = runner.invoke(
        main.app,
        ["contentful-update", "--app", "demo", "--fields", '{"appStore": false}', "--apply", "--json"],
    )

    assert result.exit_code == 0
    assert calls["fields"] == {"appStore": False}
    assert calls["apply"] is True


class FakeEntry:
    def __init__(self):
        self.fields_data = {}

    def fields(self, locale):
        return self.fields_data

    def save(self):
        pass

    def publish(self):
        pass


class FakeEntries:
    def __init__(self, existing=None):
        self.existing = existing
        self.created = None

    def all(self, query):
        return [self.existing] if self.existing else []

    def create(self, content_type, fields):
        self.created = (content_type, fields)
        return FakeEntry()


class FakeClient:
    def __init__(self, existing=None):
        self.entries_map = {"master": FakeEntries(existing)}

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

    payload = contentful.sync_app("demo", "master", "metadata/contentful-drafts", apply=True, update_machine=False)

    entries = fake_client.entries_map["master"]
    assert payload["action"] == "created"
    assert entries.created[0] == "product"
    assert entries.created[1]["key"]["en-US"] == "demo"
    assert entries.created[1]["production"]["en-US"] is False


def test_sync_app_apply_skips_when_entry_exists(repo_fixture, app_factory, monkeypatch):
    app_factory("demo")
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "token")
    fake_client = FakeClient(existing=FakeEntry())
    monkeypatch.setitem(sys.modules, "contentful_management", types.SimpleNamespace(Client=lambda token: fake_client))

    payload = contentful.sync_app("demo", "master", "metadata/contentful-drafts", apply=True, update_machine=False)

    assert payload["action"] == "exists"
    assert fake_client.entries_map["master"].created is None
