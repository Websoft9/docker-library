from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml
from jinja2 import Environment, FileSystemLoader

from libs.maintenance import load_maintenance_metadata


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_maintenance_metadata_validator_accepts_current_repository(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    data = load_maintenance_metadata()

    assert isinstance(data, dict)
    assert "defaults" in data


def test_new_app_manifest_matches_template_files():
    manifest = json.loads((REPO_ROOT / "metadata" / "templates" / "new-app" / "manifest.json").read_text(encoding="utf-8"))
    template_root = REPO_ROOT / "metadata" / "templates" / "new-app"

    expected = {
        ".env": ".env.tmpl",
        "docker-compose.yml": "docker-compose.yml.tmpl",
        "variables.json": "variables.json.tmpl",
        "README.md": "README.md.tmpl",
        "CHANGELOG.md": "CHANGELOG.md.tmpl",
        "src/.gitkeep": "src/.gitkeep",
    }

    assert manifest["generated_files"] == list(expected.keys())
    for generated, template_name in expected.items():
        assert (template_root / template_name).exists(), f"missing template for {generated}"


def test_new_app_templates_render_and_parse():
    template_root = REPO_ROOT / "metadata" / "templates" / "new-app"
    context = {
        "name": "demo-app",
        "trademark": "Demo App",
        "version": "1.0",
        "repo": "bitnami/demo-app",
        "image_url": "https://hub.docker.com/r/bitnami/demo-app/tags",
        "releases_url": "https://github.com/example/demo-app/tags",
        "compose_url": "https://raw.githubusercontent.com/example/demo-app/main/docker-compose.yml",
        "compose_env_url": "https://raw.githubusercontent.com/example/demo-app/main/.env.example",
        "github_url": "https://github.com/example/demo-app",
        "install_url": "https://example.com/install",
        "docs_json": json.dumps(["https://github.com/example/demo-app", "https://example.com/install"]),
        "has_releases": True,
        "has_compose": True,
        "has_compose_env": True,
        "has_compose_group": True,
        "has_install_url": True,
        "has_fork_url": True,
        "power_password": "dummy-password",
    }

    env = Environment(loader=FileSystemLoader(str(template_root)), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    env_text = env.get_template(".env.tmpl").render(**context)
    compose_text = env.get_template("docker-compose.yml.tmpl").render(**context)
    variables_text = env.get_template("variables.json.tmpl").render(**context)
    readme_text = env.get_template("README.md.tmpl").render(**context)
    changelog_text = env.get_template("CHANGELOG.md.tmpl").render(**context)

    assert "W9_VERSION=1.0" in env_text
    assert yaml.safe_load(compose_text)["services"]["demo-app"]["container_name"] == "$W9_ID"
    assert json.loads(variables_text)["name"] == "demo-app"
    assert "Demo App" in readme_text
    assert "# CHANGELOG" in changelog_text


def test_readme_template_renders_with_minimal_context():
    env = Environment(loader=FileSystemLoader(str(REPO_ROOT / "metadata" / "templates")), keep_trailing_newline=True)
    rendered = env.get_template("readme.jinja2").render(
        trademark="Demo App",
        name="demo-app",
        edition=[{"dist": "community", "version": ["1.0", "latest"]}],
        requirements={"memory": "1", "cpu": "1", "disk": "1", "url": "https://example.com"},
        ports=[{"purpose": "Web Console", "port": "8080"}],
        data_dirs=[{"volume": "data", "path": "/opt/data"}],
        guide="## 快速入门\nhandwritten",
        troubleshooting="## 故障\nnotes",
    )

    assert "# Demo App on Docker" in rendered
    assert "Supported versions: 1.0, latest" in rendered
    assert "W9_GUIDE_START" in rendered and "handwritten" in rendered
    assert "W9_TROUBLESHOOT_START" in rendered and "notes" in rendered
    assert "Web Console" in rendered and "8080" in rendered
    assert "packages this app from the official" in rendered
    assert "Apps run as containers; rebuild after any configuration change." in rendered


def test_new_app_schema_accepts_sample_request():
    schema = json.loads((REPO_ROOT / "metadata" / "new-app.schema.json").read_text(encoding="utf-8"))
    sample = {
        "name": "demo-app",
        "trademark": "Demo App",
        "version": "1.0",
        "repo": "bitnami/demo-app",
        "docs": {"github": "https://github.com/example/demo-app"},
    }

    jsonschema.Draft202012Validator(schema).validate(sample)


def test_repository_variables_json_have_consistent_shapes():
    for variables_path in sorted((REPO_ROOT / "apps").glob("*/variables.json")):
        data = json.loads(variables_path.read_text(encoding="utf-8"))
        assert isinstance(data.get("name"), str), f"{variables_path}: missing name"
        if "upstream" in data:
            assert isinstance(data["upstream"], dict), f"{variables_path}: upstream must be object"
            docs = data["upstream"].get("docs")
            if docs is not None:
                assert isinstance(docs, list), f"{variables_path}: upstream.docs must be list"
            for key in ("image", "releases"):
                if key in data["upstream"] and data["upstream"][key] is not None:
                    assert isinstance(data["upstream"][key], str), f"{variables_path}: upstream.{key} must be string"
            for key in ("compose_source", "config_source", "version_source"):
                if key in data["upstream"] and data["upstream"][key] is not None:
                    assert isinstance(data["upstream"][key], dict), f"{variables_path}: upstream.{key} must be object"

        if "env" in data:
            assert isinstance(data["env"], dict), f"{variables_path}: env must be object"
            first = data["env"].get("first_startup_only")
            if first is not None:
                assert isinstance(first, list) and all(isinstance(x, str) for x in first), (
                    f"{variables_path}: env.first_startup_only must be a list of strings"
                )


def test_db_lifecycle_snapshot_has_valid_structure():
    from datetime import date
    import re

    path = REPO_ROOT / "metadata" / "db-lifecycle.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(payload.get("version"), int)
    date.fromisoformat(payload["updated_at"])
    assert isinstance(payload.get("engines"), dict)

    for engine, engine_data in payload["engines"].items():
        assert isinstance(engine_data.get("source"), str)
        tracks = engine_data.get("tracks")
        assert isinstance(tracks, list)
        for track in tracks:
            assert isinstance(track.get("version"), str)
            assert isinstance(track.get("track"), str)
            assert track.get("eol") is None or isinstance(track.get("eol"), str)


def test_i18n_translation_covers_all_app_translatable_env_keys():
    import re

    from libs.drift import parse_env_file

    pattern = re.compile(r"^(W9_.*_SET|W9_LOGIN.*)$")
    translation = json.loads((REPO_ROOT / "i18n" / "translation.json").read_text(encoding="utf-8"))

    missing: dict[str, list[str]] = {}
    for env_path in sorted((REPO_ROOT / "apps").glob("*/.env")):
        env = parse_env_file(env_path)
        keys = [key for key in env if pattern.match(key) and key not in translation]
        if keys:
            missing[env_path.parent.name] = keys

    assert missing == {}, f"apps with translatable env keys missing from i18n: {missing}"
