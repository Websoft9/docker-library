from __future__ import annotations

from libs import imagestats
from libs.repo import repo_path


def _write_env(root, text: str) -> None:
    (root / ".env").write_text(text, encoding="utf-8")


def test_is_official_image():
    assert imagestats.is_official_image("docker.io", "redis")
    assert imagestats.is_official_image("docker.io", "postgres")
    assert not imagestats.is_official_image("docker.io", "bitnami/wordpress")
    assert not imagestats.is_official_image("ghcr.io", "nginx-proxy/nginx-proxy")


def test_parse_image_ref_handles_tags_digests_namespaces_and_library_prefix():
    assert imagestats.parse_image_ref("redis:7.0") == ("docker.io", "redis")
    assert imagestats.parse_image_ref("redis@sha256:abcd") == ("docker.io", "redis")
    assert imagestats.parse_image_ref("postgres:16") == ("docker.io", "postgres")
    assert imagestats.parse_image_ref("docker.io/library/nginx:latest") == ("docker.io", "nginx")
    assert imagestats.parse_image_ref("registry-1.docker.io/library/mysql:8") == ("docker.io", "mysql")
    assert imagestats.parse_image_ref("bitnami/wordpress:6") == ("docker.io", "bitnami/wordpress")
    assert imagestats.parse_image_ref("ghcr.io/foo/bar:1.0") == ("ghcr.io", "foo/bar")
    assert imagestats.parse_image_ref("quay.io/org/repo") == ("quay.io", "org/repo")
    assert imagestats.parse_image_ref("localhost:5000/app") == ("localhost:5000", "app")
    assert imagestats.parse_image_ref("gcr.io/proj/image:tag") == ("gcr.io", "proj/image")
    assert imagestats.parse_image_ref("nginx:1.25.3-alpine") == ("docker.io", "nginx")
    assert imagestats.parse_image_ref("budibase.docker.scarf.sh/budibase/apps") == (
        "budibase.docker.scarf.sh",
        "budibase/apps",
    )


def test_parse_image_ref_rejects_templates_and_empty():
    assert imagestats.parse_image_ref("{{ .Env.X }}") is None
    assert imagestats.parse_image_ref("") is None
    assert imagestats.parse_image_ref("   ") is None


def test_expand_env_resolves_values_and_reports_unknown():
    env = {"W9_REPO": "apache/activemq", "W9_VERSION": "6.3.0"}
    value, unresolved = imagestats.expand_env("${W9_REPO}:${W9_VERSION}", env)
    assert value == "apache/activemq:6.3.0"
    assert unresolved == []

    env = {"W9_REPO": "bitnami/wordpress"}
    value, unresolved = imagestats.expand_env("$W9_REPO:$W9_VERSION", env)
    assert value == "bitnami/wordpress:$W9_VERSION"
    assert unresolved == ["W9_VERSION"]

    value, unresolved = imagestats.expand_env("postgres:${W9_DB_VERSION:-16}", {})
    assert value == "postgres:16"
    assert unresolved == []


def test_parse_env_file_strips_surrounding_quotes(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text('W9_REPO="lscr.io/linuxserver/bookstack"\nW9_VERSION=24.0.0\n', encoding="utf-8")
    env = imagestats.parse_env_file(env_path)
    assert env == {"W9_REPO": "lscr.io/linuxserver/bookstack", "W9_VERSION": "24.0.0"}


def test_compute_stats_counts_unique_and_official(repo_fixture, app_factory):
    app_factory(
        "alpha",
        env="W9_REPO=redis\nW9_VERSION=7\n",
        compose=(
            "services:\n"
            "  main:\n"
            "    image: $W9_REPO:$W9_VERSION\n"
            "  db:\n"
            "    image: postgres:16\n"
            "  cache:\n"
            "    image: redis:7\n"
        ),
    )
    app_factory(
        "beta",
        env="W9_REPO=apache/activemq\nW9_VERSION=6\n",
        compose=(
            "services:\n"
            "  main:\n"
            "    image: ${W9_REPO}:${W9_VERSION}\n"
            "  extra:\n"
            "    image: ghcr.io/acme/helper:2\n"
        ),
    )

    stats = imagestats.compute_stats()

    assert stats["unique_images"] == 4
    assert stats["dockerio_images"] == 3  # redis, postgres, apache/activemq
    assert stats["docker_official_images"] == 2  # redis, postgres
    assert stats["dockerio_non_official_images"] == 1  # apache/activemq
    assert stats["docker_official_percent"] == round(100.0 * 2 / 3, 1)
    assert stats["non_dockerio_images"] == 1  # ghcr.io/acme/helper
    assert stats["references"] == 5
    assert stats["locally_built_excluded"] == 0
    assert stats["unresolved"] == []
    assert stats["scanned_apps"] == ["alpha", "beta"]


def test_compute_stats_excludes_locally_built_images(repo_fixture, app_factory):
    app_factory(
        "custom",
        env="W9_REPO=websoft9/custom\nW9_VERSION=1\n",
        compose=(
            "services:\n"
            "  app:\n"
            "    image: $W9_REPO:$W9_VERSION\n"
            "    build: .\n"
            "  db:\n"
            "    image: mariadb:11\n"
        ),
    )

    stats = imagestats.compute_stats()
    assert stats["unique_images"] == 1
    assert stats["references"] == 1
    assert stats["locally_built_excluded"] == 1
    assert stats["docker_official_images"] == 1
    assert stats["dockerio_non_official_images"] == 0


def test_compute_stats_records_unresolved_and_reports_registries(repo_fixture, app_factory):
    app_factory(
        "alpha",
        env="W9_REPO=postgres\nW9_VERSION=16\n",
        compose=(
            "services:\n"
            "  main:\n"
            "    image: $W9_REPO:$W9_VERSION\n"
            "  unknown:\n"
            "    image: example.invalid/team/tool:${MISSING_TAG}\n"
        ),
    )

    stats = imagestats.compute_stats()

    assert stats["unique_images"] == 1
    assert stats["docker_official_images"] == 1
    assert len(stats["unresolved"]) == 1
    assert stats["unresolved"][0]["variables"] == ["MISSING_TAG"]
    assert stats["registries"] == []  # docker.io is not listed; only non-docker.io registries are


def test_compute_stats_app_filter_and_archived(repo_fixture, app_factory):
    app_factory("alpha", env="W9_REPO=redis\n", compose="services:\n  a:\n    image: $W9_REPO:7\n")
    app_factory(
        "beta",
        env="W9_REPO=apache/activemq\n",
        compose="services:\n  a:\n    image: $W9_REPO:6\n",
    )
    app_factory(
        "retired",
        env="W9_REPO=ghcr.io/legacy/tool\n",
        compose="services:\n  a:\n    image: $W9_REPO:1\n",
        archived=True,
    )

    only_alpha = imagestats.compute_stats(app_filter="alpha")
    assert only_alpha["unique_images"] == 1
    assert only_alpha["docker_official_images"] == 1

    archived = imagestats.compute_stats(include_archived=True)
    assert archived["unique_images"] == 3
    assert archived["dockerio_non_official_images"] == 1  # apache/activemq
    assert archived["non_dockerio_images"] == 1  # ghcr.io/legacy/tool


def test_compute_stats_template_compose_falls_back(repo_fixture, app_factory):
    template = (
        "version: '3.6'\n"
        "{{/* comment only visible to template */}}\n"
        "x-base: &base\n"
        "  build: .\n"
        "  image: custom-built\n"
        "services:\n"
        "  web:\n"
        "    image: nginx:1.25\n"
        "  db:\n"
        "    image: postgres:16\n"
        "  {{ range $i := loop }}\n"
        "  replica-{{ $i }}:\n"
        "    <<: *base\n"
        "  {{ end }}\n"
    )
    app_factory("tpl", compose=template)

    stats = imagestats.compute_stats()

    assert stats["unique_images"] == 2
    assert stats["docker_official_images"] == 2  # nginx, postgres
    assert stats["references"] == 2
    assert stats["scanned_apps"] == ["tpl"]
