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
