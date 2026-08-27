from __future__ import annotations

import pytest

from libs import readme


def test_render_readme_writes_rendered_output(repo_fixture, app_factory, monkeypatch):
    app_factory("demo", variables={
        "name": "demo",
        "trademark": "Demo App",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0"]}],
    })
    template_root = repo_fixture / "metadata" / "templates"
    template_root.mkdir(parents=True, exist_ok=True)
    (template_root / "readme.jinja2").write_text("# {{ trademark }}\n", encoding="utf-8")
    monkeypatch.setattr(readme, "TEMPLATE_ROOT", template_root)

    result = readme.render_readme("demo")

    assert result["app"] == "demo"
    assert result["path"] == "apps/demo/README.md"
    assert (repo_fixture / "apps" / "demo" / "README.md").read_text(encoding="utf-8") == "# Demo App\n"


def test_render_readme_raises_for_missing_app():
    with pytest.raises(FileNotFoundError):
        readme.render_readme("missing")


def test_first_startup_only_note_renders_when_env_listed(repo_fixture, app_factory, monkeypatch):
    app_factory("demo", variables={
        "name": "demo",
        "trademark": "Demo App",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0"]}],
        "env": {"first_startup_only": ["W9_LOGIN_PASSWORD"]},
    })
    template_root = repo_fixture / "metadata" / "templates"
    template_root.mkdir(parents=True, exist_ok=True)
    (template_root / "readme.jinja2").write_text(
        "{% if first_startup_only_note %}{{ first_startup_only_note }}{% endif %}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(readme, "TEMPLATE_ROOT", template_root)

    readme.render_readme("demo")
    text = (repo_fixture / "apps" / "demo" / "README.md").read_text(encoding="utf-8")

    assert "`W9_LOGIN_PASSWORD` take effect on first startup only" in text


def test_first_startup_only_note_absent_without_env_node(repo_fixture, app_factory, monkeypatch):
    app_factory("demo", variables={
        "name": "demo",
        "trademark": "Demo App",
        "release": True,
        "upstream": {"image": "https://hub.docker.com/_/demo/tags"},
        "edition": [{"dist": "community", "version": ["1.0"]}],
    })
    template_root = repo_fixture / "metadata" / "templates"
    template_root.mkdir(parents=True, exist_ok=True)
    (template_root / "readme.jinja2").write_text(
        "{% if first_startup_only_note %}{{ first_startup_only_note }}{% endif %}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(readme, "TEMPLATE_ROOT", template_root)

    readme.render_readme("demo")
    text = (repo_fixture / "apps" / "demo" / "README.md").read_text(encoding="utf-8")

    assert text == "\n"


def test_references_include_ghcr_and_official_compose_sources():
    refs = readme._references({
        "upstream": {
            "image": "ghcr.io/example/app",
            "releases": "https://github.com/example/app/releases",
            "compose": {
                "compose": "https://raw.githubusercontent.com/example/app/main/docker-compose.yml",
                "env": "https://raw.githubusercontent.com/example/app/main/.env.example",
            },
            "docs": ["https://github.com/example/app", "https://example.com/docs"],
        }
    })

    assert refs == [
        {"label": "GHCR image", "url": "https://ghcr.io/example/app"},
        {"label": "Releases", "url": "https://github.com/example/app/releases"},
        {"label": "Official compose", "url": "https://raw.githubusercontent.com/example/app/main/docker-compose.yml"},
        {"label": "Official env example", "url": "https://raw.githubusercontent.com/example/app/main/.env.example"},
        {"label": "GitHub docs", "url": "https://github.com/example/app"},
        {"label": "Official docs", "url": "https://example.com/docs"},
    ]


def test_compose_volumes_deduplicates_shared_mounts():
    data_dirs, config_overrides = readme._compose_volumes(
        """
services:
  app:
    volumes:
      - shared_cache:/cache
  worker:
    volumes:
      - shared_cache:/cache
      - ./src/demo.conf:/etc/demo.conf:ro
      - ./src/demo.conf:/etc/demo.conf:ro
"""
    )

    assert data_dirs == [{"volume": "shared_cache", "path": "/cache"}]
    assert config_overrides == [{"source": "./src/demo.conf", "target": "/etc/demo.conf"}]
