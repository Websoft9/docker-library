from __future__ import annotations

import json

from jinja2 import Environment, FileSystemLoader

from libs import newapp


def test_tags_url_formats_short_repo_and_preserves_urls():
    assert newapp.tags_url("wordpress") == "wordpress"
    assert newapp.tags_url("bitnami/wordpress") == "https://hub.docker.com/r/bitnami/wordpress"
    assert newapp.tags_url("https://example.com/image") == "https://example.com/image"


def test_validate_request_uses_schema_errors(monkeypatch):
    monkeypatch.setattr(newapp, "load_schema", lambda: {
        "type": "object",
        "required": ["name", "trademark"],
        "properties": {
            "name": {"type": "string"},
            "trademark": {"type": "string"},
        },
    })

    errors = newapp.validate_request({"name": "demo"})

    assert errors == ["request: 'trademark' is a required property"]


def test_existing_app_returns_matching_item(monkeypatch):
    monkeypatch.setattr(newapp, "collect_apps", lambda include_archived=True: [{"name": "demo", "status": "active", "scope": "public"}])

    assert newapp.existing_app("demo") == {"name": "demo", "status": "active", "scope": "public"}
    assert newapp.existing_app("missing") is None


def test_scaffold_dry_run_and_write(repo_fixture, monkeypatch):
    schema_path = repo_fixture / "metadata" / "new-app.schema.json"
    template_root = repo_fixture / "metadata" / "templates" / "new-app"
    template_root.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(json.dumps({
        "type": "object",
        "required": ["name", "trademark"],
        "properties": {
            "name": {"type": "string"},
            "trademark": {"type": "string"},
            "version": {"type": "string"},
            "repo": {"type": "string"},
            "docs": {"type": "object"},
            "upstream": {"type": "object"},
        },
    }) + "\n", encoding="utf-8")
    (template_root / "manifest.json").write_text(json.dumps({"generated_files": [".env", "docker-compose.yml", "variables.json", "README.md", "CHANGELOG.md", "src/.gitkeep"]}) + "\n", encoding="utf-8")
    (template_root / ".env.tmpl").write_text("W9_VERSION={{ version }}\n", encoding="utf-8")
    (template_root / "docker-compose.yml.tmpl").write_text("services:\n", encoding="utf-8")
    (template_root / "variables.json.tmpl").write_text('{"name": "{{ name }}", "trademark": "{{ trademark }}"}', encoding="utf-8")
    (template_root / "README.md.tmpl").write_text("# {{ trademark }}\n", encoding="utf-8")
    (template_root / "CHANGELOG.md.tmpl").write_text("# CHANGELOG\n", encoding="utf-8")
    (template_root / "src").mkdir(exist_ok=True)
    (template_root / "src" / ".gitkeep").write_text("\n", encoding="utf-8")

    monkeypatch.setattr(newapp, "SCHEMA_PATH", schema_path)
    monkeypatch.setattr(newapp, "TEMPLATE_ROOT", template_root)
    monkeypatch.setattr(newapp, "TEMPLATE_ENV", Environment(loader=FileSystemLoader(str(template_root)), autoescape=False, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True))
    monkeypatch.setattr(newapp, "check_app", lambda name, gate="all": {"app": name, "ok": True})

    dry_run = newapp.scaffold("demo", "Demo", version="1.0", repo="bitnami/demo", dry_run=True)
    written = newapp.scaffold("demo", "Demo", version="1.0", repo="bitnami/demo", dry_run=False)

    assert dry_run["dry_run"] is True
    assert (repo_fixture / "apps" / "demo" / ".env").exists()
    assert (repo_fixture / "apps" / "demo" / "CHANGELOG.md").exists()
    assert written["check"] == {"app": "demo", "ok": True}
    assert "run libs app-gen-readme --app <app> after editing variables.json" in written["todo"]
