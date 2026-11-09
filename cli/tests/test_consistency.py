from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml
from jinja2 import Environment, FileSystemLoader

from libs.maintenance import load_maintenance_metadata


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_database_types_match_machine_schema():
    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    database_types = json.loads((REPO_ROOT / "metadata" / "database-types.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/databaseTypes"})
    validator.validate(database_types)


@pytest.mark.parametrize("database", [
    [],
    [{"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}]}],
    [{"id": "rds", "providers": [{"type": "external", "drivers": ["postgresql"]}],
      "datasource": {"DATABASE_URL": "${url}"}, "name": [], "users": []}],
    [{"id": "cache", "providers": [{"type": "internal", "service": "redis", "driver": "redis"}],
      "users": [{"user": "default", "password": "", "usage": ["initialization", "application"]}]}],
    {"type": "postgresql", "supported_modes": ["bundled", "external"], "bundled": {"service": "db"}},
])
def test_database_schema_accepts_declarations_and_legacy_transition(database):
    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], **schema["properties"]["database"]})
    validator.validate(database)


@pytest.mark.parametrize("component", [
    {"providers": [{"type": "internal", "service": "db", "driver": "postgresql"}]},
    {"id": "rds", "providers": []},
    {"id": "rds", "providers": [{"type": "internal", "driver": "postgresql"}]},
    {"id": "rds", "providers": [{"type": "external", "drivers": ["postgresql"]}]},
    {"id": "rds", "providers": [{"type": "external", "drivers": []}], "datasource": {"URL": "${url}"}},
    {"id": "rds", "providers": [{"type": "external", "drivers": ["postgresql"]}], "datasource": {}},
    {"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}], "name": "db"},
    {"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}],
     "users": [{"password": "${PASSWORD}"}]},
    {"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}],
     "users": [{"user": "admin", "usage": []}]},
    {"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}],
     "users": [{"user": "admin", "usage": ["application", "application"]}]},
    {"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}],
     "users": [{"user": "admin", "usage": ["root"]}]},
])
def test_database_schema_rejects_invalid_components(component):
    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/databaseComponents"})
    with pytest.raises(jsonschema.ValidationError):
        validator.validate([component])


def test_database_types_match_documented_definitions():
    database_types = json.loads((REPO_ROOT / "metadata" / "database-types.json").read_text(encoding="utf-8"))
    spec = (REPO_ROOT / "docs" / "app-database-connection-spec.md").read_text(encoding="utf-8")
    type_section = spec.split("## 3. General Type Definitions", 1)[1].split("## 4.", 1)[0]
    documented_types = json.loads(type_section.split("```json\n", 1)[1].split("```", 1)[0])
    users_schema = json.loads(spec.rsplit("```json\n", 1)[1].split("```", 1)[0])

    assert database_types == documented_types
    assert not {"sqlite", "etcd", "memcached"} & database_types.keys()
    for definition in database_types.values():
        assert definition["host"] == ""
        assert type(definition["port"]) is int
        assert 1 <= definition["port"] <= 65535
        assert definition["images"]
        assert len(definition["images"]) == len(set(definition["images"]))
        assert all(isinstance(image, str) and image for image in definition["images"])
        assert isinstance(definition["url"], str)
        if "name" in definition:
            assert isinstance(definition["name"], list)
            assert all(isinstance(name, str) for name in definition["name"])
        jsonschema.Draft202012Validator(users_schema).validate(definition["users"])


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
        "date": "2026-08-28",
    }

    env = Environment(loader=FileSystemLoader(str(template_root)), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    env_text = env.get_template(".env.tmpl").render(**context)
    compose_text = env.get_template("docker-compose.yml.tmpl").render(**context)
    variables_text = env.get_template("variables.json.tmpl").render(**context)
    readme_text = env.get_template("README.md.tmpl").render(**context)
    changelog_text = env.get_template("CHANGELOG.md.tmpl").render(**context)

    assert "W9_VERSION=1.0" in env_text
    assert yaml.safe_load(compose_text)["services"]["demo-app"]["container_name"] == "${W9_ID}"
    assert json.loads(variables_text)["name"] == "demo-app"
    assert "Demo App" in readme_text
    assert "# CHANGELOG" in changelog_text
    assert "## 2026-08-28" in changelog_text


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


def test_variables_schema_accepts_env_secrets():
    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    sample = {
        "name": "demo",
        "trademark": "Demo",
        "release": True,
        "edition": [{"dist": "community", "version": ["1.0"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
        "env": {"secrets": ["APP_KEY", "OH_KEY"], "first_startup_only": ["APP_KEY"]},
    }

    jsonschema.Draft202012Validator(schema).validate(sample)


def test_variables_schema_rejects_unknown_env_keys():
    import pytest

    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    sample = {
        "name": "demo",
        "trademark": "Demo",
        "release": True,
        "edition": [{"dist": "community", "version": ["1.0"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
        "env": {"rules": ["APP_KEY"]},
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(sample)


def test_variables_schema_accepts_setup_steps():
    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    sample = {
        "name": "demo",
        "trademark": "Demo",
        "release": True,
        "edition": [{"dist": "community", "version": ["1.0"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
        "access": {"web": {"port": 8080, "path": "/"}},
        "setup": {
            "summary": "Bootstrap this app first.",
            "steps": [
                {
                    "id": "setup-token",
                    "text": "Read the one-time token from logs.",
                    "action": {"type": "show-log", "service": "app", "tail": 50},
                },
                {
                    "id": "setup-wizard",
                    "text": "Open the setup screen.",
                    "action": {"type": "open", "access": "web", "path": "/setup"},
                },
            ],
        },
    }

    jsonschema.Draft202012Validator(schema).validate(sample)


def test_variables_schema_rejects_setup_pattern_group_model():
    import pytest

    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    sample = {
        "name": "demo",
        "trademark": "Demo",
        "release": True,
        "edition": [{"dist": "community", "version": ["1.0"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
        "setup": {
            "steps": [
                {
                    "id": "setup-token",
                    "text": "Bad old pattern model.",
                    "action": {
                        "type": "show-log",
                        "service": "app",
                        "pattern": "token=(.+)",
                        "group": 1,
                    },
                }
            ]
        },
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(sample)


def test_variables_schema_accepts_staged_credentials():
    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    sample = {
        "name": "demo",
        "trademark": "Demo",
        "release": True,
        "edition": [{"dist": "community", "version": ["1.0"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
        "credentials": {
            "initial": {
                "username": {"source": "inline", "value": "admin"},
                "password": {
                    "source": "container-log",
                    "match": "regex",
                    "pattern": "password '([^']+)'",
                    "group": 1,
                },
            },
            "login": {
                "username": {"source": "inline", "value": "admin"},
                "password": {"source": "container-env", "name": "W9_LOGIN_PASSWORD"},
            },
        },
    }

    jsonschema.Draft202012Validator(schema).validate(sample)


def test_repository_variables_json_match_schema():
    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    problems: dict[str, list[str]] = {}
    for variables_path in sorted((REPO_ROOT / "apps").glob("*/variables.json")):
        data = json.loads(variables_path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            problems[variables_path.parent.name] = [
                f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
            ]
    assert problems == {}, f"apps with variables.json schema violations: {problems}"


@pytest.mark.parametrize("app,services", [
    ("wordpress", ["wordpress"]),
    ("woocommerce", ["woocommerce", "woocommerce-bootstrap"]),
    ("wordpresspro", ["wordpress", "redis-bootstrap"]),
])
def test_wordpress_database_declaration_matches_native_inputs(app, services):
    from libs.app import collect_app_info

    target = REPO_ROOT / "apps" / app
    variables = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    components = {component["id"]: component for component in variables["database"]}
    assert len(components) == len(variables["database"])
    assert set(components) == ({"rds", "redis"} if app == "wordpresspro" else {"rds"})
    component = components["rds"]
    assert component == {
        "id": "rds",
        "providers": [
            {"type": "internal", "service": "mysql", "driver": "mysql"},
            {"type": "external", "drivers": ["mysql", "mariadb"]},
        ],
        "datasource": {
            "WORDPRESS_DB_HOST": "${host}:${port}",
            "WORDPRESS_DB_NAME": "${name}",
            "WORDPRESS_DB_USER": "${users[*].user}",
            "WORDPRESS_DB_PASSWORD": "${users[*].password}",
        },
    }
    native_inputs = set(component["datasource"])
    if app == "wordpresspro":
        assert components["redis"] == {
            "id": "redis",
            "providers": [{"type": "internal", "service": "redis", "driver": "redis"}],
            "name": ["${WP_REDIS_DATABASE}"],
            "users": [],
            "datasource": {
                "WP_REDIS_HOST": "${host}",
                "WP_REDIS_PORT": "${port}",
                "WP_REDIS_DATABASE": "${name}",
            },
        }
        native_inputs.update(components["redis"]["datasource"])
    env_keys = set(collect_app_info(app)["env_keys"])
    assert native_inputs <= env_keys
    if app == "wordpress":
        assert not (target / ".env.external-db").exists()
        assert not env_keys.intersection({
            "W9_DB_HOST_SET", "W9_DB_PORT_SET", "W9_DB_NAME_SET",
            "W9_DB_USER_SET", "W9_DB_PASSWORD_SET",
        })
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    for service_name in services:
        service = compose["services"][service_name]
        env_files = service.get("env_file", [])
        assert ".env" in ([env_files] if isinstance(env_files, str) else env_files)
        environment = service.get("environment") or {}
        if isinstance(environment, list):
            environment = dict(entry.split("=", 1) if "=" in entry else (entry, None) for entry in environment)
        for native_input in native_inputs:
            reference = "${" + native_input + "}"
            assert environment.get(native_input, reference) == reference


@pytest.mark.parametrize("app,db_service,host,name,user,password", [
    ("nextcloud", "db", "MYSQL_HOST", "MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD"),
    ("matomo", "mysql", "MATOMO_DATABASE_HOST", "MATOMO_DATABASE_DBNAME", "MATOMO_DATABASE_USERNAME", "MATOMO_DATABASE_PASSWORD"),
])
def test_native_database_inputs_preserve_defaults_and_independent_initialization(app, db_service, host, name, user, password):
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / app
    values = dotenv_values(target / ".env", interpolate=False)
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert {key: values[key] for key in [host, name, user, password]} == {
        host: "${W9_ID}-mysql",
        name: app,
        user: app,
        password: "${W9_POWER_PASSWORD}",
    }
    environment = services[app]["environment"]
    if isinstance(environment, list):
        environment = dict(entry.split("=", 1) for entry in environment)
    for native_input in [host, name, user, password]:
        assert environment[native_input] == "${" + native_input + "}"
    assert services[app]["env_file"] == ".env"
    assert services[db_service]["environment"] == {
        "MYSQL_DATABASE": app,
        "MYSQL_USER": app,
        "MYSQL_PASSWORD": "${W9_POWER_PASSWORD}",
        "MYSQL_ROOT_PASSWORD": "${W9_POWER_PASSWORD}",
    }
    database = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database == [{
        "id": "mysql",
        "providers": [
            {"type": "internal", "service": db_service, "driver": "mysql"},
            {"type": "external", "drivers": ["mysql", "mariadb"]},
        ],
        "datasource": {
            host: "${host}", name: "${name}",
            user: "${users[*].user}", password: "${users[*].password}",
        },
    }]
    if app == "matomo":
        assert values["MATOMO_DATABASE_ADAPTER"] == "mysql"


def test_kong_database_initialization_and_healthcheck_are_independent_of_application_inputs():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "kong"
    values = dotenv_values(target / ".env", interpolate=False)
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert values["POSTGRES_DB"] == values["KONG_PG_DATABASE"] == "kong"
    assert values["POSTGRES_USER"] == values["KONG_PG_USER"] == "kong"
    assert values["POSTGRES_PASSWORD"] == values["KONG_PG_PASSWORD"] == "${W9_POWER_PASSWORD}"
    assert values["KONG_PG_HOST"] == "${W9_ID}-postgresql"
    assert values["KONG_DATABASE"] == "postgres"
    assert services["db"]["environment"] == {
        "POSTGRES_DB": "${POSTGRES_DB}",
        "POSTGRES_USER": "${POSTGRES_USER}",
        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}",
    }
    assert services["db"]["healthcheck"]["test"] == [
        "CMD", "pg_isready", "-d", "${POSTGRES_DB}", "-U", "${POSTGRES_USER}",
    ]
    assert services["kong-migrations"]["command"] == "kong migrations bootstrap"
    assert services["kong-migrations-up"]["command"][-1] == "kong migrations up && kong migrations finish"
    assert services["kong"]["depends_on"]["kong-migrations-up"]["condition"] == "service_completed_successfully"


def test_airflow_native_database_urls_reach_all_consumers_with_independent_initialization():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "airflow"
    values = dotenv_values(target / ".env", interpolate=False)
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    inputs = {
        "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": "postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${W9_ID}-postgres/${POSTGRES_DB}",
        "AIRFLOW__CELERY__RESULT_BACKEND": "db+postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${W9_ID}-postgres/${POSTGRES_DB}",
    }
    assert {key: values[key] for key in inputs} == inputs
    consumers = {name for name in services if name.startswith("airflow-")}
    assert consumers == {
        "airflow-apiserver", "airflow-scheduler", "airflow-dag-processor", "airflow-worker",
        "airflow-triggerer", "airflow-init", "airflow-cli",
    }
    for consumer in consumers:
        environment = services[consumer]["environment"]
        for native_input in inputs:
            assert environment[native_input] == "${" + native_input + "}"
        assert environment["AIRFLOW__CELERY__BROKER_URL"] == "redis://:@${W9_ID}-redis:6379/0"
    assert services["postgres"]["environment"] == {
        "POSTGRES_USER": "${POSTGRES_USER}",
        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}",
        "POSTGRES_DB": "${POSTGRES_DB}",
    }
    assert services["airflow-init"]["environment"]["_AIRFLOW_DB_MIGRATE"] == "true"
    for service, job in (("airflow-dag-processor", "DagProcessorJob"), ("airflow-triggerer", "TriggererJob")):
        assert services[service]["healthcheck"]["test"] == [
            "CMD-SHELL", f'/entrypoint airflow jobs check --job-type {job} --hostname "$${{HOSTNAME}}"',
        ]
        assert services[service]["healthcheck"]["timeout"] == "10s"
    worker_probe = services["airflow-worker"]["healthcheck"]["test"]
    assert worker_probe[0] == "CMD-SHELL"
    assert worker_probe[1].startswith("/entrypoint bash -c '")
    assert worker_probe[1].endswith("'")
    assert 'inspect ping -d "celery@$${HOSTNAME}"' in worker_probe[1]
    assert services["airflow-worker"]["healthcheck"]["timeout"] == "10s"
    database = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database == [
        {
            "id": "postgres",
            "providers": [
                {"type": "internal", "service": "postgres", "driver": "postgresql"},
                {"type": "external", "drivers": ["postgresql"]},
            ],
            "datasource": {
                "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": "postgresql+psycopg2://${users[*].user}:${users[*].password}@${host}:${port}/${name}",
                "AIRFLOW__CELERY__RESULT_BACKEND": "db+postgresql://${users[*].user}:${users[*].password}@${host}:${port}/${name}",
            },
        },
        {
            "id": "redis",
            "providers": [{"type": "internal", "service": "redis", "driver": "redis"}],
            "name": ["0"], "users": [],
        },
    ]


def test_phpmyadmin_optional_database_uses_password_source_and_existing_host_alias():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "phpmyadmin"
    values = dotenv_values(target / ".env", interpolate=False)
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert values["MYSQL_ROOT_PASSWORD"] == "${W9_POWER_PASSWORD}"
    has_password_seed = bool(values["W9_POWER_PASSWORD"])
    assert has_password_seed
    assert values["PMA_HOST"] == "mysql"
    assert values["PMA_PORT"] == "3306"
    assert "COMPOSE_PROFILES" not in values
    assert services["phpmyadmin"]["env_file"] == ".env"
    assert "depends_on" not in services["phpmyadmin"]
    assert services["db"]["profiles"] == ["db"]
    assert services["db"]["environment"] == {"MYSQL_ROOT_PASSWORD": "${MYSQL_ROOT_PASSWORD}"}
    assert services["db"]["networks"]["default"]["aliases"] == ["mysql"]
    database = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database == [{
        "id": "mariadb",
        "providers": [{"type": "internal", "service": "db", "driver": "mariadb"}],
        "name": [],
        "users": [{"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["administration"]}],
        "datasource": {"PMA_HOST": "${host}", "PMA_PORT": "${port}"},
    }]


def test_thingsboard_native_database_inputs_and_file_marker_initialization():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "thingsboard"
    values = dotenv_values(target / ".env", interpolate=False)
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert values["POSTGRES_DB"] == "thingsboard"
    assert values["POSTGRES_USER"] == values["SPRING_DATASOURCE_USERNAME"] == "postgres"
    password_defaults_match = values["POSTGRES_PASSWORD"] == values["SPRING_DATASOURCE_PASSWORD"]
    assert password_defaults_match
    assert values["SPRING_DATASOURCE_URL"] == "jdbc:postgresql://${W9_ID}-postgres:5432/thingsboard"
    assert not any(key.startswith("POSTGRESQL_") for key in values)
    assert set(services) == {"thingsboard-ce", "postgres", "tb-web-report"}
    for consumer in ["thingsboard-ce"]:
        assert services[consumer]["env_file"] == [".env"]
        environment = dict(entry.split("=", 1) for entry in services[consumer]["environment"])
        for native_input in ["SPRING_DATASOURCE_URL", "SPRING_DATASOURCE_USERNAME", "SPRING_DATASOURCE_PASSWORD"]:
            assert environment[native_input] == "${" + native_input + "}"
        assert services[consumer]["depends_on"]["postgres"]["condition"] == "service_healthy"
    assert services["postgres"]["environment"] == [
        "POSTGRES_USER=${POSTGRES_USER}", "POSTGRES_DB=${POSTGRES_DB}", "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}",
    ]
    assert services["postgres"]["healthcheck"]["test"] == [
        "CMD", "pg_isready", "-U", "${POSTGRES_USER}", "-d", "${POSTGRES_DB}",
    ]
    assert services["thingsboard-ce"]["depends_on"] == {"postgres": {"condition": "service_healthy"}}
    assert services["thingsboard-ce"]["entrypoint"] == ["bash", "/bootstrap/init.sh"]
    assert "./src:/bootstrap:ro" in services["thingsboard-ce"]["volumes"]
    assert "license-data:/data" in services["thingsboard-ce"]["volumes"]
    assert not any("bootstrap-state" in volume for volume in services["thingsboard-ce"]["volumes"])
    assert services["tb-web-report"]["image"] == "thingsboard/tb-web-report:${W9_VERSION}"
    assert services["tb-web-report"]["environment"]["HTTP_BIND_PORT"] == 8383
    assert services["thingsboard-ce"]["ports"] == ["${W9_HTTP_PORT_SET}:8080"]
    assert "/data/.tb-installed" in services["thingsboard-ce"]["healthcheck"]["test"][-1]
    assert not any(service.get("ports") for name, service in services.items() if name != "thingsboard-ce")
    assert "REPORTS_SERVER_ENDPOINT_URL=http://${W9_ID}-web-report:8383" in services["thingsboard-ce"]["environment"]
    initializer = (target / "src" / "init.sh").read_text(encoding="utf-8")
    assert "set -euo pipefail" in initializer
    assert "INSTALL_TB=true UPGRADE_TB=false /usr/bin/start-tb-node.sh" in initializer
    assert "exec /usr/bin/start-tb-node.sh" in initializer
    assert "psql" not in initializer
    assert "case " not in initializer
    assert initializer.index("mkdir /data/.tb-installing") < initializer.index("INSTALL_TB=true UPGRADE_TB=false")
    assert initializer.index("touch /data/.tb-installed") > initializer.index("INSTALL_TB=true UPGRADE_TB=false")
    assert not (target / "src" / "InstallState.java").exists()
    database = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database == [{
        "id": "postgres",
        "providers": [
            {"type": "internal", "service": "postgres", "driver": "postgresql"},
            {"type": "external", "drivers": ["postgresql"]},
        ],
        "datasource": {
            "SPRING_DATASOURCE_URL": "jdbc:postgresql://${host}:${port}/${name}",
            "SPRING_DATASOURCE_USERNAME": "${users[*].user}",
            "SPRING_DATASOURCE_PASSWORD": "${users[*].password}",
        },
    }]


@pytest.mark.parametrize("scenario", ["fresh_and_recreate", "installer_failure", "existing_marker", "interrupted_install"])
def test_thingsboard_file_marker_startup(tmp_path, scenario):
    import os
    import subprocess

    data = tmp_path / "data"
    data.mkdir()
    installed = data / ".tb-installed"
    installing = data / ".tb-installing"
    calls = tmp_path / "calls"
    upstream = tmp_path / "upstream.sh"
    upstream.write_text(
        '#!/usr/bin/env bash\nset -eu\n'
        'printf "%s:%s:%s\\n" "${INSTALL_TB:-normal}" "${UPGRADE_TB:-unset}" "${LOAD_DEMO:-unset}" >> "$CALL_LOG"\n'
        'if [[ "${INSTALL_TB:-}" == true ]]; then exit "$INSTALL_EXIT_CODE"; fi\n',
        encoding="utf-8",
    )
    upstream.chmod(0o755)
    script = (REPO_ROOT / "apps" / "thingsboard" / "src" / "init.sh").read_text(encoding="utf-8")
    script = script.replace("/data/", str(data) + "/").replace("/usr/bin/start-tb-node.sh", str(upstream))
    environment = {**os.environ, "CALL_LOG": str(calls), "INSTALL_EXIT_CODE": "7" if scenario == "installer_failure" else "0",
                   "INSTALL_TB": "true", "UPGRADE_TB": "true", "LOAD_DEMO": "true"}
    if scenario == "existing_marker":
        installed.touch()
    if scenario == "interrupted_install":
        installing.mkdir()
    result = subprocess.run(["bash", "-c", script], env=environment, capture_output=True, text=True, timeout=5)
    if scenario in {"installer_failure", "interrupted_install"}:
        assert result.returncode == (7 if scenario == "installer_failure" else 1)
        assert not installed.exists()
        assert installing.is_dir()
        before = calls.read_text() if calls.exists() else ""
        retried = subprocess.run(["bash", "-c", script], env=environment, capture_output=True, text=True, timeout=5)
        assert retried.returncode == 1
        assert (calls.read_text() if calls.exists() else "") == before
    else:
        assert result.returncode == 0, result.stderr
        assert installed.is_file()
        assert not installing.exists()
        expected = ["normal:unset:unset"]
        if scenario == "fresh_and_recreate":
            expected.insert(0, "true:false:unset")
            recreated = subprocess.run(["bash", "-c", script], env=environment, capture_output=True, text=True, timeout=5)
            assert recreated.returncode == 0, recreated.stderr
            expected.append("normal:unset:unset")
        assert calls.read_text().splitlines() == expected


def test_database_coverage_ledger_accounts_for_every_active_app():
    import re

    specification = (REPO_ROOT / "docs" / "app-database-connection-spec.md").read_text(encoding="utf-8")
    section = specification.split("### 1.2 ", 1)[1].split("\n### ", 1)[0]
    groups = {}
    listed_apps = []
    for line in section.splitlines():
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) != 4 or not columns[1].isdigit():
            continue
        status = columns[0].strip("`")
        assert status not in groups
        apps = re.findall(r"`([a-z0-9]+)`", columns[2])
        assert len(apps) == int(columns[1]), status
        groups[status] = apps
        listed_apps.extend(apps)
    assert set(groups) == {
        "declared", "deferred-runtime", "deferred-policy", "deferred-source",
        "excluded-product", "excluded-sqlite", "excluded-internal", "excluded-client", "excluded-tool",
    }
    assert len(listed_apps) == len(set(listed_apps))
    active_apps = {path.name for path in (REPO_ROOT / "apps").iterdir() if path.is_dir()}
    assert set(listed_apps) == active_apps
    for status, apps in groups.items():
        for app in apps:
            variables = json.loads((REPO_ROOT / "apps" / app / "variables.json").read_text(encoding="utf-8"))
            if status == "declared":
                assert isinstance(variables.get("database"), list) and variables["database"], app
            else:
                assert "database" not in variables, (status, app)


def test_all_declared_database_apps_pass_non_deployment_quality_gates():
    from libs.validate import check_app

    failures = {}
    declared = []
    for path in sorted((REPO_ROOT / "apps").glob("*/variables.json")):
        variables = json.loads(path.read_text(encoding="utf-8"))
        if not variables.get("database"):
            continue
        declared.append(path.parent.name)
        report = check_app(path.parent.name)
        failed_gates = {
            gate: report[gate].get("errors", [])
            for gate in ["structure", "policy", "database_metadata"]
            if not report[gate]["ok"]
        }
        if failed_gates:
            failures[path.parent.name] = failed_gates
    assert declared
    assert failures == {}


def test_database_deployment_followup_matches_documented_scope_and_declarations():
    import re

    specification = (REPO_ROOT / "docs" / "app-database-connection-spec.md").read_text(encoding="utf-8")
    section = specification.split("### 1.4 ", 1)[1].split("\n## ", 1)[0]
    runtime_section = section.split("#### 1.4.1 ", 1)[1].split("\n#### ", 1)[0]
    expected_runtime = {
        "activepieces", "airflow", "akeneo", "canvas", "dify", "erpnext", "kong",
        "matomo", "nextcloud", "phpmyadmin", "superset", "thingsboard", "typo3",
    }
    runtime_apps = []
    for line in runtime_section.splitlines():
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) != 4 or not re.fullmatch(r"`[a-z0-9]+`", columns[0]):
            continue
        app = columns[0].strip("`")
        runtime_apps.append(app)
        files = re.findall(r"`([^`]+)`", columns[1])
        assert files and all((REPO_ROOT / "apps" / app / filename).is_file() for filename in files), app
        assert columns[2] and columns[3], app
    assert len(runtime_apps) == len(set(runtime_apps))
    assert set(runtime_apps) == expected_runtime
    metadata_section = section.split("#### 1.4.2 ", 1)[1].split("\n\n", 1)[1].split("\n\n", 1)[0]
    external_section = section.split("#### 1.4.3 ", 1)[1].split("\n#### ", 1)[0]
    metadata_apps = re.findall(r"`([a-z0-9]+)`", metadata_section)
    external_apps = re.findall(r"`([a-z0-9]+)`", external_section)
    declared = set()
    external = set()
    for path in (REPO_ROOT / "apps").glob("*/variables.json"):
        components = json.loads(path.read_text(encoding="utf-8")).get("database")
        if not components:
            continue
        declared.add(path.parent.name)
        if any(provider["type"] == "external" for component in components for provider in component["providers"]):
            external.add(path.parent.name)
    assert len(metadata_apps) == len(set(metadata_apps))
    assert set(metadata_apps).isdisjoint(expected_runtime)
    assert set(metadata_apps) | expected_runtime == declared
    assert len(external_apps) == len(set(external_apps))
    assert set(external_apps) == external


@pytest.mark.parametrize("app", [
    "postgresql", "pgvector", "timescaledb", "mysql", "mariadb",
    "mongodb", "redis", "clickhouse", "couchdb",
])
def test_standalone_database_products_do_not_declare_themselves(app):
    from libs.validate import _database_metadata_result

    target = REPO_ROOT / "apps" / app
    variables = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    assert "database" not in variables
    result = _database_metadata_result(target)
    assert result["ok"] and result["status"] == "not_applicable", result


@pytest.mark.parametrize("app", ["n8n", "keycloak", "gitea", "onlyofficedocs", "strapi", "jfrog", "umbraco"])
def test_embedded_storage_apps_do_not_invent_database_services(app):
    from dotenv import dotenv_values
    from libs.validate import _database_metadata_result

    target = REPO_ROOT / "apps" / app
    variables = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    assert set(compose["services"]) == {app}
    assert "database" not in variables
    result = _database_metadata_result(target)
    assert result["ok"] and result["status"] == "not_applicable", result
    if app == "strapi":
        values = dotenv_values(target / ".env", interpolate=False)
        assert values["DATABASE_FILENAME"] == ".tmp/data.db"
        assert "DATABASE_CLIENT" not in values
        assert "DATABASE_HOST" not in values
    elif app == "jfrog":
        values = dotenv_values(target / ".env", interpolate=False)
        assert values["JF_SHARED_DATABASE_TYPE"] == "derby"
        assert values["JF_SHARED_DATABASE_ALLOWNONPOSTGRESQL"] == "true"
    elif app == "umbraco":
        values = dotenv_values(target / ".env", interpolate=False)
        is_sqlite = "sqlite" in values["UMBRACO_DB_DSN"].lower()
        assert is_sqlite


@pytest.mark.parametrize("app,consumers,expected_services", [
    ("activepieces", ["activepieces", "worker"], {"postgres": "postgresql", "redis": "redis"}),
    ("litellm", ["litellm"], {"postgresql": "postgresql"}),
    ("lobehub", ["lobehub"], {"postgresql": "postgresql", "redis": "redis"}),
    ("mautic", ["mautic_web", "mautic_cron", "mautic_worker"], {"db": "mysql"}),
    ("typo3", ["typo3"], {"mysql": "mysql"}),
    ("ghost", ["ghost"], {"mysql": "mysql"}),
    ("redmine", ["redmine"], {"mysql": "mysql"}),
    ("dolibarr", ["dolibarr"], {"mariadb": "mariadb"}),
    ("directus", ["directus"], {"postgresql": "postgresql", "cache": "redis"}),
    ("espocrm", ["espocrm", "espocrm-daemon"], {"mariadb": "mariadb"}),
    ("metabase", ["metabase"], {"postgres": "postgresql"}),
    ("moodle", ["moodle"], {"mariadb": "mariadb"}),
    ("prestashop", ["prestashop"], {"mysql": "mysql"}),
    ("semaphoreui", ["semaphoreui"], {"mysql": "mysql"}),
    ("xwiki", ["xwiki"], {"db": "mysql"}),
    ("sonarqube", ["app"], {"db": "postgresql"}),
    ("mattermost", ["mattermost"], {"postgres": "postgresql"}),
    ("nextcloud", ["nextcloud"], {"db": "mysql"}),
    ("matomo", ["matomo"], {"mysql": "mysql"}),
    ("phpmyadmin", ["phpmyadmin"], {"db": "mariadb"}),
    ("thingsboard", ["thingsboard-ce"], {"postgres": "postgresql"}),
    ("kong", ["kong", "kong-migrations", "kong-migrations-up"], {"db": "postgresql"}),
    ("seafile", ["seafile"], {"db": "mariadb", "redis": "redis"}),
    ("umami", ["umami"], {"postgresql": "postgresql"}),
    ("odoo", ["odoo"], {"postgresql": "postgresql"}),
    ("langfuse", ["langfuse-web", "langfuse-worker"], {"postgres": "postgresql", "clickhouse": "clickhouse", "redis": "redis"}),
    ("vaultwarden", ["vaultwarden"], {"mariadb": "mariadb"}),
    ("chatwoot", ["rails", "sidekiq"], {"postgres": "postgresql", "redis": "redis"}),
    ("inngest", ["inngest"], {"postgresql": "postgresql", "redis": "redis"}),
    ("zentao", ["zentao"], {"mysql": "mysql"}),
    ("zulip", ["zulip"], {"database": "postgresql", "redis": "redis"}),
    ("ckan", ["ckan-base"], {"db": "postgresql", "solr": "solr", "redis": "redis"}),
    ("zammad", ["zammad-nginx", "zammad-init", "zammad-railsserver", "zammad-scheduler", "zammad-websocket"], {
        "zammad-postgresql": "postgresql", "zammad-elasticsearch": "elasticsearch", "zammad-redis": "redis",
    }),
    ("budibase", ["app-service", "worker-service", "proxy-service", "litellm-service"], {
        "couchdb-service": "couchdb", "redis-service": "redis", "litellm-db": "postgresql",
    }),
    ("akeneo", ["akeneo", "worker"], {"mysql": "mysql", "elasticsearch": "elasticsearch"}),
    ("librechat", ["api", "rag_api"], {"mongodb": "mongodb", "meilisearch": "meilisearch", "vectordb": "postgresql"}),
    ("openwebui", ["app"], {"chroma": "chroma"}),
    ("wazuh", ["wazuh.manager", "wazuh.dashboard"], {"wazuh.indexer": "opensearch"}),
    ("canvas", ["web", "jobs"], {"postgresql": "postgresql", "redis": "redis"}),
    ("superset", ["superset", "superset-init", "superset-worker", "superset-worker-beat"], {"db": "postgresql", "redis": "redis"}),
])
def test_standard_database_migrations_match_existing_inputs(app, consumers, expected_services):
    from libs.app import collect_app_info

    target = REPO_ROOT / "apps" / app
    variables = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    components = variables["database"]
    assert isinstance(components, list) and components
    internal = {
        provider["service"]: provider["driver"]
        for component in components for provider in component["providers"]
        if provider["type"] == "internal"
    }
    assert internal == expected_services
    inputs = {
        native_input for component in components
        for native_input in component.get("datasource", {})
    }
    assert inputs.isdisjoint({
        "database__client", "DB_CLIENT", "MB_DB_TYPE", "MOODLE_DATABASE_TYPE",
        "SEMAPHORE_DB_DIALECT", "KONG_DATABASE", "MM_SQLSETTINGS_DRIVERNAME", "DATABASE_TYPE",
    })
    if app == "kong":
        assert components[0]["providers"] == [
            {"type": "internal", "service": "db", "driver": "postgresql"},
            {"type": "external", "drivers": ["postgresql"]},
        ]
    if app == "mattermost":
        assert components[0]["datasource"]["MM_SQLSETTINGS_DATASOURCE"] == "${url}?sslmode=disable&connect_timeout=10"
    if app == "moodle":
        assert components[0]["name"] == ["${MYSQL_DATABASE}"]
        assert {account["password"] for account in components[0]["users"]} == {"${MYSQL_ROOT_PASSWORD}", "${MYSQL_PASSWORD}"}
    assert inputs <= set(collect_app_info(app)["env_keys"])
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    for consumer in consumers:
        service = compose["services"][consumer]
        env_files = service.get("env_file", [])
        assert ".env" in ([env_files] if isinstance(env_files, str) else env_files)
        environment = service.get("environment") or {}
        if isinstance(environment, list):
            environment = dict(entry.split("=", 1) if "=" in entry else (entry, None) for entry in environment)
        for native_input in inputs:
            reference = "${" + native_input + "}"
            assert environment.get(native_input, reference) == reference


def test_mautic_database_declaration_uses_existing_consumers_and_independent_initialization():
    from libs.validate import check_app

    target = REPO_ROOT / "apps" / "mautic"
    database, = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "db", "driver": "mysql"},
        {"type": "external", "drivers": ["mysql"]},
    ]
    assert database["datasource"] == {
        "MAUTIC_DB_HOST": "${host}", "MAUTIC_DB_PORT": "${port}", "MAUTIC_DB_DATABASE": "${name}",
        "MAUTIC_DB_USER": "${users[*].user}", "MAUTIC_DB_PASSWORD": "${users[*].password}",
    }
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert services["db"]["environment"] == {
        "MYSQL_DATABASE": "mautic", "MYSQL_USER": "mautic",
        "MYSQL_PASSWORD": "${W9_POWER_PASSWORD}", "MYSQL_ROOT_PASSWORD": "${W9_POWER_PASSWORD}",
    }
    report = check_app("mautic")
    assert report["structure"]["ok"] and report["policy"]["ok"] and report["database_metadata"]["ok"]


def test_typo3_database_inputs_preserve_first_install_and_login_pair():
    from dotenv import dotenv_values
    from libs.validate import check_app

    target = REPO_ROOT / "apps" / "typo3"
    variables = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    database, = variables["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "mysql", "driver": "mysql"},
        {"type": "external", "drivers": ["mysql"]},
    ]
    assert database["datasource"] == {
        "TYPO3_DB_HOST": "${host}", "TYPO3_DB_PORT": "${port}", "TYPO3_DB_DBNAME": "${name}",
        "TYPO3_DB_USERNAME": "${users[*].user}", "TYPO3_DB_PASSWORD": "${users[*].password}",
    }
    assert set(database["datasource"]) <= set(variables["env"]["first_startup_only"])
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["W9_LOGIN_USER"] == "admin"
    assert values["TYPO3_SETUP_ADMIN_USERNAME"] == "${W9_LOGIN_USER}"
    assert values["TYPO3_SETUP_ADMIN_PASSWORD"] == "${W9_LOGIN_PASSWORD}"
    assert values["TYPO3_DB_DRIVER"] == "mysqli" and "TYPO3_DB_DRIVER" not in database["datasource"]
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert services["mysql"]["environment"] == {
        "MYSQL_DATABASE": "typo3", "MYSQL_USER": "typo3",
        "MYSQL_PASSWORD": "${W9_POWER_PASSWORD}", "MYSQL_ROOT_PASSWORD": "${W9_POWER_PASSWORD}",
    }
    report = check_app("typo3")
    assert report["structure"]["ok"] and report["policy"]["ok"] and report["database_metadata"]["ok"]


def test_dify_internal_database_sources_keep_main_and_plugin_databases_distinct():
    from dotenv import dotenv_values
    from libs.validate import check_app

    target = REPO_ROOT / "apps" / "dify"
    database, redis, vector = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "db", "driver": "postgresql"},
    ]
    assert database["name"] == ["${POSTGRES_DB}", "${DB_PLUGIN_DATABASE}"]
    assert database["users"] == [{"user": "postgres", "password": "${POSTGRES_PASSWORD}"}]
    assert all("datasource" not in component for component in [database, redis, vector])
    assert redis["providers"] == [{"type": "internal", "service": "redis", "driver": "redis"}]
    assert redis["name"] == ["0", "1"] and "users" not in redis
    assert vector == {
        "id": "weaviate", "providers": [{"type": "internal", "service": "weaviate", "driver": "weaviate"}],
    }
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    for consumer in ["api", "worker", "plugin_daemon"]:
        for native_input in ["DB_HOST", "DB_PORT", "DB_USERNAME", "DB_PASSWORD"]:
            assert services[consumer]["environment"][native_input] == "${" + native_input + "}"
    for consumer in ["api", "worker"]:
        assert services[consumer]["environment"]["DB_DATABASE"] == "${DB_DATABASE}"
    assert services["plugin_daemon"]["environment"]["DB_DATABASE"] == "${DB_PLUGIN_DATABASE}"
    assert services["db"]["environment"] == {
        "PGUSER": "${PGUSER}", "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}",
        "POSTGRES_DB": "${POSTGRES_DB}", "PGDATA": "${PGDATA:-/var/lib/postgresql/data/pgdata}",
    }
    assert "env_file" not in services["db"]
    assert "env_file" not in services["redis"]
    assert services["redis"]["environment"] == {
        "REDIS_PASSWORD": "${REDIS_PASSWORD}", "REDISCLI_AUTH": "${REDIS_PASSWORD:-difyai123456}",
    }
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["DB_PORT"] == "5432"
    assert values["REDIS_PORT"] == "6379"
    assert values["WEAVIATE_ENDPOINT"] == "http://${W9_ID}-weaviate:8080"
    assert values["PGUSER"] == "${DB_USERNAME}" and values["POSTGRES_DB"] == "${DB_DATABASE}"
    assert values["POSTGRES_PASSWORD"] == "${DB_PASSWORD}"
    report = check_app("dify")
    assert report["structure"]["ok"] and report["policy"]["ok"] and report["database_metadata"]["ok"]


@pytest.mark.parametrize("app", ["supabase", "erpnext", "dify", "budibase", "jitsu", "librechat", "graylog"])
def test_complex_bundled_database_declarations_are_information_only(app):
    from libs.validate import _database_metadata_result

    target = REPO_ROOT / "apps" / app
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert components
    for component in components:
        assert all(provider["type"] == "internal" for provider in component["providers"])
        assert "datasource" not in component
    readme = (target / "README.md").read_text(encoding="utf-8")
    assert "does not offer external databases" in readme
    report = _database_metadata_result(target)
    assert report["ok"] and report["status"] == "ok", report


def test_graylog_declares_known_mongodb_without_guessing_managed_search_connection():
    from dotenv import dotenv_values
    from libs.validate import check_app

    target = REPO_ROOT / "apps" / "graylog"
    variables = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    assert variables["database"] == [{
        "id": "mongodb", "providers": [{"type": "internal", "service": "mongodb", "driver": "mongodb"}],
        "name": ["graylog"], "users": [],
    }]
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["GRAYLOG_MONGODB_URI"] == "mongodb://${W9_ID}-mongodb:27017/graylog"
    assert services["graylog"]["environment"]["GRAYLOG_MONGODB_URI"] == "${GRAYLOG_MONGODB_URI}"
    assert services["datanode"]["environment"]["GRAYLOG_DATANODE_MONGODB_URI"] == "${GRAYLOG_MONGODB_URI}"
    assert "environment" not in services["mongodb"] and "env_file" not in services["mongodb"]
    assert "managed Data Node" in variables["help"]["db"]
    report = check_app("graylog")
    assert report["structure"]["ok"] and report["policy"]["ok"] and report["database_metadata"]["ok"]


def test_kibana_optional_backend_preserves_unconfigured_default_and_native_host_array():
    from dotenv import dotenv_values
    from libs.validate import check_app

    target = REPO_ROOT / "apps" / "kibana"
    database, = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database == {
        "id": "elasticsearch", "providers": [{"type": "external", "drivers": ["elasticsearch"]}],
        "datasource": {"ELASTICSEARCH_HOSTS": '["${url}"]'},
    }
    values = dotenv_values(target / ".env", interpolate=False)
    assert "ELASTICSEARCH_HOSTS" not in values
    assert "ELASTICSEARCH_SERVICEACCOUNTTOKEN" not in values
    assert '# ELASTICSEARCH_HOSTS=["http://elasticsearch:9200"]' in (target / ".env").read_text(encoding="utf-8")
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert set(services) == {"kibana"}
    assert services["kibana"]["env_file"] == ".env"
    assert "ELASTICSEARCH_HOSTS" not in (services["kibana"].get("environment") or {})
    report = check_app("kibana")
    assert report["structure"]["ok"] and report["policy"]["ok"] and report["database_metadata"]["ok"]


def test_activepieces_database_initialization_is_independent_of_application_inputs():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "activepieces"
    database, redis = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "postgres", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]},
    ]
    assert database["datasource"] == {
        "AP_POSTGRES_HOST": "${host}", "AP_POSTGRES_PORT": "${port}",
        "AP_POSTGRES_DATABASE": "${name}", "AP_POSTGRES_USERNAME": "${users[*].user}",
        "AP_POSTGRES_PASSWORD": "${users[*].password}",
    }
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert services["postgres"]["environment"] == {
        "POSTGRES_DB": "activepieces", "POSTGRES_USER": "postgres", "POSTGRES_PASSWORD": "${W9_POWER_PASSWORD}",
    }
    assert "env_file" not in services["postgres"]
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["AP_POSTGRES_DATABASE"] == "activepieces"
    assert values["AP_POSTGRES_USERNAME"] == "postgres"
    assert values["AP_POSTGRES_PASSWORD"] == "${W9_POWER_PASSWORD}"
    assert values["AP_DB_TYPE"] == "POSTGRES" and "AP_DB_TYPE" not in database["datasource"]
    assert redis["providers"] == [{"type": "internal", "service": "redis", "driver": "redis"}]
    assert redis["users"] == []
    assert "command" not in services["redis"]


def test_litellm_database_url_keeps_bundled_initialization_independent():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "litellm"
    database, = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "postgresql", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]},
    ]
    assert database["datasource"] == {
        "DATABASE_URL": "postgresql://${users[*].user}:${users[*].password}@${host}:${port}/${name}",
    }
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert services["postgresql"]["environment"] == {
        "POSTGRES_USER": "litellm", "POSTGRES_DB": "litellm", "POSTGRES_PASSWORD": "${W9_POWER_PASSWORD}",
    }
    assert "env_file" not in services["postgresql"]
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["DATABASE_URL"] == "postgresql://litellm:${W9_POWER_PASSWORD}@${W9_ID}-postgresql:5432/litellm"
    config = yaml.safe_load((target / "src" / "proxy_server_config.yaml").read_text(encoding="utf-8"))
    assert config["general_settings"].get("database_url") in [None, "os.environ/DATABASE_URL"]


def test_lobehub_database_url_preserves_extensions_and_auxiliary_stores():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "lobehub"
    database, redis = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "postgresql", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]},
    ]
    assert database["datasource"] == {
        "DATABASE_URL": "postgresql://${users[*].user}:${users[*].password}@${host}:${port}/${name}",
    }
    services = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))["services"]
    assert services["postgresql"]["environment"] == {
        "POSTGRES_DB": "${LOBE_DB_NAME}", "POSTGRES_USER": "postgres", "POSTGRES_PASSWORD": "${W9_POWER_PASSWORD}",
    }
    assert "env_file" not in services["postgresql"]
    assert services["postgresql"]["command"] == ["postgres", "-c", "shared_preload_libraries=pg_search,pg_cron"]
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["DATABASE_URL"] == "postgresql://postgres:${W9_POWER_PASSWORD}@${W9_ID}-postgresql:5432/lobechat"
    assert values["LOBE_DB_NAME"] == "lobechat"
    assert redis["providers"] == [{"type": "internal", "service": "redis", "driver": "redis"}]
    assert redis["users"] == []
    assert redis["datasource"] == {"REDIS_URL": "redis://${host}:${port}"}
    assert services["redis"]["command"] == "redis-server --save 60 1000 --appendonly yes"
    assert services["rustfs-init"]["depends_on"] == {"rustfs": {"condition": "service_healthy"}}


def test_seafile_database_declaration_preserves_multiple_names_and_initialization():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "seafile"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    database, cache = components
    assert database["providers"] == [
        {"type": "internal", "service": "db", "driver": "mariadb"},
        {"type": "external", "drivers": ["mariadb", "mysql"]},
    ]
    assert database["name"] == [
        "${SEAFILE_MYSQL_DB_CCNET_DB_NAME}",
        "${SEAFILE_MYSQL_DB_SEAFILE_DB_NAME}",
        "${SEAFILE_MYSQL_DB_SEAHUB_DB_NAME}",
    ]
    assert database["users"] == [
        {"user": "root", "password": "${INIT_SEAFILE_MYSQL_ROOT_PASSWORD}", "usage": ["initialization", "administration"]},
        {"user": "${SEAFILE_MYSQL_DB_USER}", "password": "${SEAFILE_MYSQL_DB_PASSWORD}", "usage": ["application"]},
    ]
    assert database["datasource"] == {
        "SEAFILE_MYSQL_DB_HOST": "${host}",
        "SEAFILE_MYSQL_DB_PORT": "${port}",
        "SEAFILE_MYSQL_DB_USER": "${users[*].user}",
        "SEAFILE_MYSQL_DB_PASSWORD": "${users[*].password}",
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    assert "MYSQL_ROOT_PASSWORD=${INIT_SEAFILE_MYSQL_ROOT_PASSWORD}" in compose["services"]["db"]["environment"]
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["INIT_SEAFILE_MYSQL_ROOT_PASSWORD"] == "${W9_POWER_PASSWORD}"
    assert values["SEAFILE_MYSQL_DB_PASSWORD"] == "${W9_POWER_PASSWORD}"
    assert values["CACHE_PROVIDER"] == "redis"
    assert cache["providers"] == [{"type": "internal", "service": "redis", "driver": "redis"}]
    assert "users" not in cache
    assert cache["datasource"] == {
        "REDIS_HOST": "${host}", "REDIS_PORT": "${port}", "REDIS_PASSWORD": "${users[*].password}",
    }
    assert compose["services"]["redis"]["environment"] == ["REDIS_PASSWORD=${REDIS_PASSWORD}"]
    assert '--requirepass "$${REDIS_PASSWORD}"' in compose["services"]["redis"]["command"][-1]


def test_umami_database_declaration_matches_script_created_account():
    from dotenv import dotenv_values
    from urllib.parse import urlsplit

    target = REPO_ROOT / "apps" / "umami"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert len(components) == 1
    database = components[0]
    assert database["providers"] == [
        {"type": "internal", "service": "postgresql", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]},
    ]
    assert "name" not in database
    assert database["users"] == [
        {"user": "${POSTGRES_USER}", "password": "${POSTGRES_PASSWORD}", "usage": ["initialization", "administration"]},
        {"user": "umami", "password": "${W9_RCODE}", "usage": ["application"]},
    ]
    assert database["datasource"] == {"DATABASE_URL": "${url}"}
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    service = compose["services"]["postgresql"]
    assert service["environment"] == {
        "POSTGRES_DB": "umami", "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "${W9_POWER_PASSWORD}", "POSTGRES_UMAMI_PASSWORD": "${W9_RCODE}",
    }
    assert "./src/postgresql_init.sh:/docker-entrypoint-initdb.d/postgresql_init.sh" in service["volumes"]
    script = (target / "src" / "postgresql_init.sh").read_text(encoding="utf-8")
    assert '--username "$POSTGRES_USER"' in script
    assert "CREATE USER umami WITH PASSWORD '${POSTGRES_UMAMI_PASSWORD}'" in script
    values = dotenv_values(target / ".env", interpolate=False)
    connection = urlsplit(values["DATABASE_URL"])
    assert connection.username == "umami"
    assert connection.password == "${W9_RCODE}"
    assert connection.path == "/umami"


def test_odoo_database_declaration_preserves_dynamic_database_support():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "odoo"
    variables = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    components = variables["database"]
    assert not (target / ".env.external-db").exists()
    assert "external-db installation override" not in variables["help"]["db"]
    assert components == [{
        "id": "postgres",
        "providers": [
            {"type": "internal", "service": "postgresql", "driver": "postgresql"},
            {"type": "external", "drivers": ["postgresql"]},
        ],
        "datasource": {
            "HOST": "${host}", "PORT": "${port}",
            "USER": "${users[*].user}", "PASSWORD": "${users[*].password}",
        },
    }]
    assert not any(key in variables["help"]["db"] for key in components[0]["datasource"])
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    values = dotenv_values(target / ".env", interpolate=False)
    assert not set(values).intersection({
        "W9_DB_HOST_SET", "W9_DB_PORT_SET", "W9_DB_NAME_SET",
        "W9_DB_USER_SET", "W9_DB_PASSWORD_SET",
    })
    assert compose["services"]["odoo"]["env_file"] == ".env"
    service = compose["services"]["postgresql"]
    assert values["HOST"] == service["container_name"]
    assert values["PORT"] == "5432"
    assert values["USER"] == service["environment"]["POSTGRES_USER"]
    assert values["PASSWORD"] == service["environment"]["POSTGRES_PASSWORD"] == "${W9_POWER_PASSWORD}"


def test_langfuse_database_declaration_matches_internal_storage_sources():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "langfuse"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert components == [
        {"id": "postgres", "providers": [{"type": "internal", "service": "postgres", "driver": "postgresql"}]},
        {"id": "clickhouse", "providers": [{"type": "internal", "service": "clickhouse", "driver": "clickhouse"}]},
        {
            "id": "redis", "providers": [{"type": "internal", "service": "redis", "driver": "redis"}],
            "users": [{"user": "default", "password": "${REDIS_AUTH}", "usage": ["application"]}],
        },
    ]
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    values = dotenv_values(target / ".env", interpolate=False)
    for service, keys in [
        ("postgres", ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]),
        ("clickhouse", ["CLICKHOUSE_DB", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD"]),
    ]:
        for key in keys:
            assert services[service]["environment"][key] == "${" + key + "}"
            assert values[key]
    assert "--requirepass ${REDIS_AUTH}" in services["redis"]["command"]
    assert "REDIS_AUTH" not in services["redis"].get("environment", {})
    assert values["REDIS_AUTH"]


def test_vaultwarden_database_declaration_preserves_mysql_aliases_and_password_source():
    from dotenv import dotenv_values
    from urllib.parse import urlsplit

    target = REPO_ROOT / "apps" / "vaultwarden"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert components == [{
        "id": "mariadb",
        "providers": [
            {"type": "internal", "service": "mariadb", "driver": "mariadb"},
            {"type": "external", "drivers": ["mysql", "mariadb"]},
        ],
        "name": ["${MYSQL_DATABASE}"],
        "users": [
            {"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["administration"]},
            {"user": "${MYSQL_USER}", "password": "${MYSQL_PASSWORD}", "usage": ["application"]},
        ],
        "datasource": {"DATABASE_URL": "mysql://${users[*].user}:${users[*].password}@${host}:${port}/${name}"},
    }]
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    service = compose["services"]["mariadb"]
    environment = dict(entry.split("=", 1) for entry in service["environment"])
    assert environment == {
        "MYSQL_ROOT_PASSWORD": "${W9_RCODE}", "MYSQL_PASSWORD": "${W9_RCODE}",
        "MYSQL_DATABASE": "vaultwarden", "MYSQL_USER": "vaultwarden",
    }
    connection = urlsplit(dotenv_values(target / ".env", interpolate=False)["DATABASE_URL"])
    assert connection.scheme == "mysql"
    assert connection.username == environment["MYSQL_USER"]
    assert connection.password == environment["MYSQL_PASSWORD"]
    assert connection.path == "/" + environment["MYSQL_DATABASE"]
    assert connection.netloc.rsplit("@", 1)[1] == service["container_name"] + ":3306"


@pytest.mark.parametrize("app,service,expected_datasource", [
    ("chatwoot", "postgres", {
        "POSTGRES_HOST": "${host}", "POSTGRES_DATABASE": "${name}",
        "POSTGRES_USERNAME": "${users[*].user}", "POSTGRES_PASSWORD": "${users[*].password}",
    }),
    ("inngest", "postgresql", {"INNGEST_POSTGRES_URI": "${url}"}),
])
def test_native_postgresql_declarations_keep_redis_independent(app, service, expected_datasource):
    from dotenv import dotenv_values
    from urllib.parse import urlsplit

    target = REPO_ROOT / "apps" / app
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    database, cache = components
    assert database == {
        "id": "postgres",
        "providers": [
            {"type": "internal", "service": service, "driver": "postgresql"},
            {"type": "external", "drivers": ["postgresql"]},
        ],
        "datasource": expected_datasource,
    }
    cache_input = "REDIS_URL" if app == "chatwoot" else "INNGEST_REDIS_URI"
    assert cache == {
        "id": "redis", "providers": [{"type": "internal", "service": "redis", "driver": "redis"}],
        "users": [], "datasource": {cache_input: "redis://${host}:${port}"},
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    environment = compose["services"][service]["environment"]
    if isinstance(environment, list):
        environment = dict(entry.split("=", 1) for entry in environment)
    assert environment["POSTGRES_DB"] == app
    assert environment["POSTGRES_PASSWORD"] == "${W9_POWER_PASSWORD}"
    values = dotenv_values(target / ".env", interpolate=False)
    if app == "chatwoot":
        assert values["POSTGRES_HOST"] == compose["services"][service]["container_name"]
        assert values["POSTGRES_DATABASE"] == environment["POSTGRES_DB"]
        assert values["POSTGRES_USERNAME"] == environment["POSTGRES_USER"]
        assert values["POSTGRES_PASSWORD"] == environment["POSTGRES_PASSWORD"]
    else:
        connection = urlsplit(values["INNGEST_POSTGRES_URI"])
        assert connection.username == environment["POSTGRES_USER"]
        assert connection.password == environment["POSTGRES_PASSWORD"]
        assert connection.path == "/" + environment["POSTGRES_DB"]
        assert not connection.query
    assert urlsplit(values[cache_input]).password is None
    assert "--requirepass" not in json.dumps(compose["services"]["redis"].get("command", []))


def test_zentao_database_declaration_matches_root_only_native_inputs():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "zentao"
    database = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"][0]
    assert database["providers"] == [
        {"type": "internal", "service": "mysql", "driver": "mysql"},
        {"type": "external", "drivers": ["mysql"]},
    ]
    assert database["users"] == [
        {"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["application", "administration"]},
    ]
    assert database["datasource"] == {
        "ZT_MYSQL_HOST": "${host}", "ZT_MYSQL_PORT": "${port}", "ZT_MYSQL_DB": "${name}",
        "ZT_MYSQL_USER": "${users[*].user}", "ZT_MYSQL_PASSWORD": "${users[*].password}",
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    environment = compose["services"]["mysql"]["environment"]
    assert environment == {"MYSQL_DATABASE": "zentao", "MYSQL_ROOT_PASSWORD": "${W9_POWER_PASSWORD}"}
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["ZT_MYSQL_USER"] == "root"
    assert values["ZT_MYSQL_DB"] == environment["MYSQL_DATABASE"]
    assert values["ZT_MYSQL_PASSWORD"] == environment["MYSQL_ROOT_PASSWORD"]


def test_zulip_database_declaration_preserves_authenticated_redis_source():
    target = REPO_ROOT / "apps" / "zulip"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert components == [
        {"id": "postgres", "providers": [{"type": "internal", "service": "database", "driver": "postgresql"}]},
        {"id": "redis", "providers": [{"type": "internal", "service": "redis", "driver": "redis"}]},
    ]
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    redis = compose["services"]["redis"]
    assert redis["environment"]["REDIS_PASSWORD"] == "${W9_POWER_PASSWORD}"
    assert "requirepass '$$REDIS_PASSWORD'" in redis["command"][-1]
    database_types = json.loads((REPO_ROOT / "metadata" / "database-types.json").read_text(encoding="utf-8"))
    assert database_types["redis"]["users"] == [{"user": "default", "password": "${REDIS_PASSWORD}"}]


def test_ckan_database_declaration_matches_multiple_roles_and_script_created_names():
    from dotenv import dotenv_values
    from urllib.parse import urlsplit

    target = REPO_ROOT / "apps" / "ckan"
    database, search, cache = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["name"] == ["${CKAN_POSTGRES_DB}", "${CKAN_DATASTORE_POSTGRES_DB}", "ckan_test", "datastore_test"]
    assert database["users"] == [
        {"user": "${POSTGRES_USER}", "password": "${POSTGRES_PASSWORD}", "usage": ["initialization", "administration"]},
        {"user": "${CKAN_POSTGRES_USER}", "password": "${CKAN_POSTGRES_USER_PWD}", "usage": ["application"]},
        {"user": "${CKAN_DATASTORE_POSTGRES_WRITE_USER}", "password": "${CKAN_DATASTORE_POSTGRES_WRITE_PWD}", "usage": ["application"]},
        {"user": "${CKAN_DATASTORE_POSTGRES_READ_USER}", "password": "${CKAN_DATASTORE_POSTGRES_READ_PWD}", "usage": ["application"]},
    ]
    assert database["providers"] == [
        {"type": "internal", "service": "db", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]},
    ]
    values = dotenv_values(target / ".env", interpolate=False)
    for native_input, user, password, name in [
        ("CKAN_SQLALCHEMY_URL", "CKAN_POSTGRES_USER", "CKAN_POSTGRES_USER_PWD", "CKAN_POSTGRES_DB"),
        ("CKAN_DATASTORE_WRITE_URL", "CKAN_DATASTORE_POSTGRES_WRITE_USER", "CKAN_DATASTORE_POSTGRES_WRITE_PWD", "CKAN_DATASTORE_POSTGRES_DB"),
        ("CKAN_DATASTORE_READ_URL", "CKAN_DATASTORE_POSTGRES_READ_USER", "CKAN_DATASTORE_POSTGRES_READ_PWD", "CKAN_DATASTORE_POSTGRES_DB"),
    ]:
        assert database["datasource"][native_input] == "postgresql://${users[*].user}:${users[*].password}@${host}:${port}/${name}"
        connection = urlsplit(values[native_input])
        assert connection.username == values[user]
        assert connection.password == values[password]
        assert connection.path == "/" + values[name]
    scripts = target / "src" / "postgresql" / "docker-entrypoint-initdb.d"
    assert 'CREATE DATABASE "$CKAN_POSTGRES_DB"' in (scripts / "10_create_ckandb.sh").read_text(encoding="utf-8")
    assert 'CREATE DATABASE "$CKAN_DATASTORE_POSTGRES_DB"' in (scripts / "20_create_datastore.sh").read_text(encoding="utf-8")
    tests = (scripts / "30_setup_test_databases.sh").read_text(encoding="utf-8")
    assert "CREATE DATABASE ckan_test" in tests
    assert "CREATE DATABASE datastore_test" in tests
    assert search["providers"] == [{"type": "internal", "service": "solr", "driver": "solr"}]
    assert search["name"] == ["ckan"] and search["users"] == []
    assert search["datasource"] == {"CKAN_SOLR_URL": "http://${host}:${port}/solr/${name}"}
    assert urlsplit(values["CKAN_SOLR_URL"]).path == "/solr/ckan"
    assert cache["providers"] == [{"type": "internal", "service": "redis", "driver": "redis"}]
    assert cache["users"] == []
    assert cache["name"] == ["1", "${CKAN__HARVEST__MQ__REDIS_DB}"]
    assert values["CKAN__HARVEST__MQ__REDIS_DB"]
    assert urlsplit(values["CKAN_REDIS_URL"]).path == "/1"


def test_zammad_database_declaration_matches_bootstrap_role_and_search_security():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "zammad"
    database, search, cache = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["name"] == ["${ZAMMAD_DB}"]
    assert database["users"] == [
        {"user": "${POSTGRES_USER}", "password": "${POSTGRES_PASSWORD}", "usage": ["initialization", "administration"]},
        {"user": "${ZAMMAD_DB_USER}", "password": "${ZAMMAD_DB_PASS}", "usage": ["application"]},
    ]
    assert database["providers"] == [
        {"type": "internal", "service": "zammad-postgresql", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]},
    ]
    assert database["datasource"] == {
        "POSTGRESQL_HOST": "${host}", "POSTGRESQL_PORT": "${port}", "POSTGRESQL_DB": "${name}",
        "POSTGRESQL_USER": "${users[*].user}", "POSTGRESQL_PASS": "${users[*].password}",
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    environment = compose["services"]["zammad-postgresql"]["environment"]
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["POSTGRESQL_DB"] == environment["ZAMMAD_DB"]
    assert values["POSTGRESQL_USER"] == environment["ZAMMAD_DB_USER"]
    assert values["POSTGRESQL_PASS"] == environment["ZAMMAD_DB_PASS"] == "${W9_RCODE}"
    script = (target / "src" / "postgresql_init.sh").read_text(encoding="utf-8")
    assert '--variable role="${ZAMMAD_DB_USER}"' in script
    assert '--variable pass="${ZAMMAD_DB_PASS}"' in script
    assert '--variable db="${ZAMMAD_DB}"' in script
    assert search["providers"] == [{"type": "internal", "service": "zammad-elasticsearch", "driver": "elasticsearch"}]
    assert search["users"] == []
    assert compose["services"]["zammad-elasticsearch"]["environment"]["xpack.security.enabled"] == "false"
    assert "ELASTICSEARCH_SCHEMA" not in search["datasource"]
    assert cache["providers"] == [{"type": "internal", "service": "zammad-redis", "driver": "redis"}]
    assert cache["users"] == []
    assert "--requirepass" not in json.dumps(compose["services"]["zammad-redis"].get("command", []))


def test_supabase_database_declaration_matches_current_base_stack_roles_and_shared_database_instance():
    target = REPO_ROOT / "apps" / "supabase"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert len(components) == 1
    database = components[0]
    assert database["providers"] == [
        {"type": "internal", "service": "db", "driver": "postgresql"},
    ]
    assert database["name"] == ["${POSTGRES_DB}", "_supabase"]
    assert "datasource" not in database
    accounts = {account["user"]: account for account in database["users"]}
    assert len(accounts) == len(database["users"]) == 7
    assert accounts == {
        "postgres": {"user": "postgres", "password": "${POSTGRES_PASSWORD}", "usage": ["application", "administration"]},
        "supabase_admin": {"user": "supabase_admin", "password": "${POSTGRES_PASSWORD}", "usage": ["application"]},
        "authenticator": {"user": "authenticator", "password": "${POSTGRES_PASSWORD}", "usage": ["application"]},
        "pgbouncer": {"user": "pgbouncer", "password": "${POSTGRES_PASSWORD}", "usage": ["application"]},
        "supabase_auth_admin": {"user": "supabase_auth_admin", "password": "${POSTGRES_PASSWORD}", "usage": ["application"]},
        "supabase_functions_admin": {"user": "supabase_functions_admin", "password": "${POSTGRES_PASSWORD}"},
        "supabase_storage_admin": {"user": "supabase_storage_admin", "password": "${POSTGRES_PASSWORD}", "usage": ["application"]},
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert services["db"]["environment"]["POSTGRES_DB"] == services["db"]["environment"]["PGDATABASE"] == "${POSTGRES_DB}"
    assert services["db"]["environment"]["POSTGRES_PASSWORD"] == services["db"]["environment"]["PGPASSWORD"] == "${POSTGRES_PASSWORD}"
    assert services["db"]["environment"]["POSTGRES_PORT"] == services["db"]["environment"]["PGPORT"] == "${POSTGRES_PORT}"
    assert "POSTGRES_USER" not in services["db"]["environment"]
    assert "./src/db/_supabase.sql:/docker-entrypoint-initdb.d/migrations/97-_supabase.sql:ro" in services["db"]["volumes"]
    assert "./src/db/roles.sql:/docker-entrypoint-initdb.d/init-scripts/99-roles.sql:ro" in services["db"]["volumes"]
    scripts = target / "src" / "db"
    assert "CREATE DATABASE _supabase WITH OWNER :pguser;" in (scripts / "_supabase.sql").read_text(encoding="utf-8")
    roles = (scripts / "roles.sql").read_text(encoding="utf-8")
    assert '\\set pgpass `echo "$POSTGRES_PASSWORD"`' in roles
    for role in ["authenticator", "pgbouncer", "supabase_auth_admin", "supabase_functions_admin", "supabase_storage_admin"]:
        assert "ALTER USER " + role + " WITH PASSWORD :'pgpass';" in roles
    for consumer, native_input, protocol, user, name in [
        ("auth", "GOTRUE_DB_DATABASE_URL", "postgres", "supabase_auth_admin", "${POSTGRES_DB}"),
        ("rest", "PGRST_DB_URI", "postgres", "authenticator", "${POSTGRES_DB}"),
        ("storage", "DATABASE_URL", "postgres", "supabase_storage_admin", "${POSTGRES_DB}"),
        ("functions", "SUPABASE_DB_URL", "postgresql", "postgres", "${POSTGRES_DB}"),
        ("supavisor", "DATABASE_URL", "ecto", "supabase_admin", "_supabase"),
    ]:
        assert services[consumer]["environment"][native_input] == (
            protocol + "://" + user + ":${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/" + name
        )
    for consumer, user_key, password_key in [
        ("studio", "POSTGRES_USER_READ_WRITE", "POSTGRES_PASSWORD"),
        ("meta", "PG_META_DB_USER", "PG_META_DB_PASSWORD"),
        ("realtime", "DB_USER", "DB_PASSWORD"),
    ]:
        expected_user = "supabase_admin" if consumer == "realtime" else "postgres"
        assert services[consumer]["environment"][user_key] == expected_user
        assert services[consumer]["environment"][password_key] == "${POSTGRES_PASSWORD}"
    pooler = (target / "src" / "pooler" / "pooler.exs").read_text(encoding="utf-8")
    for native_input, parameter in [("POSTGRES_HOST", "db_host"), ("POSTGRES_PORT", "db_port"), ("POSTGRES_DB", "db_database")]:
        assert '"' + parameter + '" => System.get_env("' + native_input + '")' in pooler
        for consumer in ["studio", "supavisor"]:
            assert services[consumer]["environment"][native_input] == "${" + native_input + "}"
    assert '"db_user" => "pgbouncer"' in pooler
    assert '"db_password" => System.get_env("POSTGRES_PASSWORD")' in pooler
    assert "\\c _supabase" in (scripts / "pooler.sql").read_text(encoding="utf-8")
    metadata = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    assert metadata["env"]["first_startup_only"] == ["POSTGRES_PASSWORD"]
    assert "external databases are not offered" in metadata["help"]["db"]
    readme = (target / "README.md").read_text(encoding="utf-8")
    assert "Note: `POSTGRES_PASSWORD`" in readme
    assert "does not offer external databases" in readme


def test_superset_database_declaration_matches_script_created_databases_and_accounts():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "superset"
    database, cache = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "db", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]},
    ]
    assert database["name"] == ["${POSTGRES_DB}", "${EXAMPLES_DB}", "superset_cypress"]
    assert database["users"] == [
        {"user": "${POSTGRES_USER}", "password": "${POSTGRES_PASSWORD}", "usage": ["application", "initialization", "administration"]},
        {"user": "${EXAMPLES_USER}", "password": "${EXAMPLES_PASSWORD}", "usage": ["application"]},
    ]
    assert database["datasource"] == {
        "DATABASE_HOST": "${host}", "DATABASE_PORT": "${port}", "DATABASE_DB": "${name}",
        "DATABASE_USER": "${users[*].user}", "DATABASE_PASSWORD": "${users[*].password}",
        "EXAMPLES_HOST": "${host}", "EXAMPLES_PORT": "${port}", "EXAMPLES_DB": "${name}",
        "EXAMPLES_USER": "${users[*].user}", "EXAMPLES_PASSWORD": "${users[*].password}",
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    initialization = compose["services"]["db"]["environment"]
    assert initialization == [
        "POSTGRES_DB=${POSTGRES_DB}", "POSTGRES_USER=${POSTGRES_USER}", "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}",
        "EXAMPLES_DB=examples", "EXAMPLES_HOST=${W9_ID}-postgresql", "EXAMPLES_USER=examples",
        "EXAMPLES_PASSWORD=${W9_POWER_PASSWORD}", "EXAMPLES_PORT=5432",
    ]
    assert "./src/docker/docker-entrypoint-initdb.d:/docker-entrypoint-initdb.d" in compose["services"]["db"]["volumes"]
    scripts = target / "src" / "docker" / "docker-entrypoint-initdb.d"
    examples = (scripts / "examples-init.sh").read_text(encoding="utf-8")
    assert "CREATE USER ${EXAMPLES_USER} WITH PASSWORD '${EXAMPLES_PASSWORD}'" in examples
    assert "CREATE DATABASE ${EXAMPLES_DB}" in examples
    assert "CREATE DATABASE superset_cypress" in (scripts / "cypress-init.sh").read_text(encoding="utf-8")
    configuration = (target / "src" / "docker" / "pythonpath_dev" / "superset_config.py").read_text(encoding="utf-8")
    for native_input in database["datasource"]:
        assert 'os.getenv("' + native_input + '"' in configuration
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["POSTGRES_DB"] == values["DATABASE_DB"] == "superset"
    assert values["POSTGRES_USER"] == values["DATABASE_USER"] == "superset"
    assert values["POSTGRES_PASSWORD"] == values["DATABASE_PASSWORD"] == values["EXAMPLES_PASSWORD"] == "${W9_POWER_PASSWORD}"
    assert "/app/docker/pythonpath_dev" in values["PYTHONPATH"].split(":")
    assert cache == {
        "id": "redis", "providers": [{"type": "internal", "service": "redis", "driver": "redis"}],
        "name": ["0", "1"], "users": [], "datasource": {"REDIS_HOST": "${host}", "REDIS_PORT": "${port}"},
    }
    assert 'os.getenv("REDIS_CELERY_DB", "0")' in configuration
    assert 'os.getenv("REDIS_RESULTS_DB", "1")' in configuration
    assert not {"REDIS_CELERY_DB", "REDIS_RESULTS_DB"} & values.keys()
    assert not compose["services"]["redis"].get("command")


def test_superset_mounted_docker_scripts_preserve_image_healthcheck():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "superset"
    assert dotenv_values(target / ".env", interpolate=False)["SUPERSET_LOAD_EXAMPLES"] == "no"
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    for service in ["superset", "superset-init", "superset-worker", "superset-worker-beat"]:
        assert "./src/docker:/app/docker" in compose["services"][service]["volumes"]
    scripts = target / "src" / "docker"
    probe = scripts / "docker-healthcheck.sh"
    assert probe.stat().st_mode & 0o111
    assert 'curl -f "http://localhost:${SUPERSET_PORT}/${SUPERSET_APP_ROOT/\\//}/health" || exit 1' in probe.read_text(encoding="utf-8")
    bootstrap = (scripts / "docker-bootstrap.sh").read_text(encoding="utf-8")
    postgres_condition = next(line for line in bootstrap.splitlines() if line.startswith('if [[ "${DATABASE_DIALECT}"'))
    assert '! python -c "import psycopg2"' in postgres_condition
    assert '"${1}"' not in postgres_condition


def test_erpnext_database_declaration_preserves_dynamic_sites_and_distinct_redis_instances():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "erpnext"
    database, cache, queue = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database == {
        "id": "mariadb", "providers": [
            {"type": "internal", "service": "mariadb", "driver": "mariadb"},
        ],
        "name": [], "users": [{"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["initialization", "administration"]}],
    }
    for component, service in [(cache, "redis-cache"), (queue, "redis-queue")]:
        assert component == {"id": service, "providers": [{"type": "internal", "service": service, "driver": "redis"}], "users": []}
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert services["mariadb"]["environment"] == {"MYSQL_ROOT_PASSWORD": "${W9_POWER_PASSWORD}"}
    assert services["mariadb"]["healthcheck"]["test"] == [
        "CMD", "healthcheck.sh", "--connect", "--innodb_initialized",
    ]
    for service in ["redis-cache", "redis-queue"]:
        assert not services[service].get("command") and not services[service].get("environment")
    for consumer in ["backend", "configurator", "create-site", "queue-long", "queue-short", "scheduler", "websocket"]:
        assert "sites:/home/frappe/frappe-bench/sites" in services[consumer]["volumes"]
    assert services["configurator"]["environment"]["DB_HOST"] == "${W9_ID}-mariadb"
    assert services["configurator"]["environment"]["DB_PORT"] == "3306"
    assert ".env" in services["create-site"]["env_file"]
    assert services["configurator"]["environment"]["REDIS_CACHE"] == "${W9_ID}-redis-cache:6379"
    assert services["configurator"]["environment"]["REDIS_QUEUE"] == "${W9_ID}-redis-queue:6379"
    configuration = services["configurator"]["command"][0]
    assert 'bench set-config -g db_host "$${DB_HOST}"' in configuration
    assert 'bench set-config -gp db_port "$${DB_PORT}"' in configuration
    assert 'bench set-config -g redis_cache "redis://$${REDIS_CACHE}"' in configuration
    assert 'bench set-config -g redis_queue "redis://$${REDIS_QUEUE}"' in configuration
    script = (target / "src" / "create-site.sh").read_text(encoding="utf-8")
    assert "bench new-site" in script and "--db-root-username=root" in script
    assert 'wait-for-it -t 120 "${W9_ID}-mariadb:3306"' in script
    assert '--db-root-password="${W9_POWER_PASSWORD}"' in script
    assert '--admin-password="${W9_LOGIN_PASSWORD}"' in script
    assert "--db-name" not in script
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["W9_LOGIN_PASSWORD"] == "${W9_POWER_PASSWORD}"
    assert not {"DB_HOST", "DB_PORT", "DB_PASSWORD"} & values.keys()


@pytest.mark.parametrize("existing_site", [False, True])
def test_erpnext_initializer_uses_bundled_database_and_separate_admin_password(tmp_path, existing_site):
    import os
    import subprocess
    import sys

    target = REPO_ROOT / "apps" / "erpnext"
    (tmp_path / "apps" / "hrms").mkdir(parents=True)
    (tmp_path / "sites").mkdir()
    if existing_site:
        (tmp_path / "sites" / "frontend").mkdir()
    binary_directory = tmp_path / "bin"
    binary_directory.mkdir()
    stub = "#!" + sys.executable + "\n" + '''import json
import os
import sys
from pathlib import Path

command = Path(sys.argv[0]).name
arguments = sys.argv[1:]
with open(os.environ["COMMAND_LOG"], "a") as output:
    output.write(json.dumps({"command": command, "args": arguments}) + "\\n")
if command == "jq":
    document = json.load(sys.stdin)
    print(document.get(arguments[-1].split()[0].lstrip("."), ""))
elif command == "bench":
    if arguments[0] == "set-config":
        configuration = Path("sites/common_site_config.json")
        document = json.loads(configuration.read_text()) if configuration.exists() else {}
        document[arguments[-2]] = int(arguments[-1]) if "-gp" in arguments else arguments[-1]
        configuration.write_text(json.dumps(document))
    elif arguments[0] == "new-site":
        Path("sites/frontend").mkdir(exist_ok=True)
    elif arguments == ["--site", "frontend", "list-apps"]:
        print("hrms")
'''
    for command in ["bench", "wait-for-it", "jq"]:
        executable = binary_directory / command
        executable.write_text(stub, encoding="utf-8")
        executable.chmod(0o755)
    environment = {
        **os.environ, "PATH": str(binary_directory) + os.pathsep + os.environ["PATH"],
        "COMMAND_LOG": str(tmp_path / "commands.jsonl"), "W9_ID": "erpnext",
        "DB_HOST": "erpnext-mariadb", "DB_PORT": "3306",
        "W9_LOGIN_PASSWORD": "application-admin-password", "W9_POWER_PASSWORD": "bundled-initialization-password",
        "REDIS_CACHE": "erpnext-redis-cache:6379", "REDIS_QUEUE": "erpnext-redis-queue:6379", "SOCKETIO_PORT": "9000",
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    configuration = compose["services"]["configurator"]["command"][0].replace("$$", "$")
    subprocess.run(["bash", "-c", configuration], cwd=tmp_path, env=environment, capture_output=True, check=True, timeout=10)
    shared = json.loads((tmp_path / "sites" / "common_site_config.json").read_text(encoding="utf-8"))
    assert shared["db_host"] == environment["DB_HOST"]
    assert shared["db_port"] == 3306
    assert shared["redis_cache"] == "redis://erpnext-redis-cache:6379"
    assert shared["redis_queue"] == shared["redis_socketio"] == "redis://erpnext-redis-queue:6379"
    subprocess.run(["bash", str(target / "src" / "create-site.sh")], cwd=tmp_path, env=environment, capture_output=True, check=True, timeout=10)
    commands = [json.loads(line) for line in (tmp_path / "commands.jsonl").read_text(encoding="utf-8").splitlines()]
    waits = [command["args"][-1] for command in commands if command["command"] == "wait-for-it"]
    assert waits == ["erpnext-mariadb:3306", "erpnext-redis-cache:6379", "erpnext-redis-queue:6379"]
    site_calls = [command["args"] for command in commands if command["command"] == "bench" and command["args"][0] == "new-site"]
    if existing_site:
        assert not site_calls
    else:
        assert len(site_calls) == 1
        assert "--db-root-username=root" in site_calls[0]
        assert "--db-root-password=bundled-initialization-password" in site_calls[0]
        assert "--admin-password=application-admin-password" in site_calls[0]
        assert not any(argument.startswith("--db-name") for argument in site_calls[0])


def test_canvas_database_inputs_match_templates_with_independent_initialization():
    from dotenv import dotenv_values
    from urllib.parse import urlsplit

    target = REPO_ROOT / "apps" / "canvas"
    database, cache = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "postgresql", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]},
    ]
    assert database["datasource"] == {
        "CANVAS_DATABASE_HOST": "${host}", "CANVAS_DATABASE_USERNAME": "${users[*].user}",
        "CANVAS_DATABASE_PRODUCTION": "${name}", "POSTGRES_PASSWORD": "${users[*].password}",
    }
    configuration = (target / "src" / "database.yml").read_text(encoding="utf-8")
    for native_input in database["datasource"]:
        assert "ENV.fetch('" + native_input + "'" in configuration
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    assert compose["services"]["postgresql"]["environment"] == {
        "POSTGRES_PASSWORD": "${W9_POWER_PASSWORD}", "POSTGRES_DB": "${POSTGRES_DB}", "POSTGRES_USER": "${POSTGRES_USER}",
    }
    assert "env_file" not in compose["services"]["postgresql"]
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["CANVAS_DATABASE_PRODUCTION"] == values["POSTGRES_DB"]
    assert values["CANVAS_DATABASE_USERNAME"] == values["POSTGRES_USER"]
    assert values["POSTGRES_PASSWORD"] == "${W9_POWER_PASSWORD}"
    assert cache == {
        "id": "redis", "providers": [{"type": "internal", "service": "redis", "driver": "redis"}],
        "users": [], "datasource": {"CANVAS_REDIS_URL": "redis://${host}:${port}"},
    }
    assert compose["services"]["redis"]["command"] == ["redis-server", "--appendonly", "yes"]
    assert "ENV.fetch('CANVAS_REDIS_URL'" in (target / "src" / "redis.yml").read_text(encoding="utf-8")
    connection = urlsplit(values["CANVAS_REDIS_URL"])
    assert connection.scheme == "redis" and not connection.username and not connection.password and not connection.path
    script = (target / "src" / "entrypoint.sh").read_text(encoding="utf-8")
    assert "bundle exec rake db:initial_setup" in script and "bundle exec rake db:migrate" in script
    assert compose["services"]["jobs"]["environment"]["CANVAS_SKIP_BOOTSTRAP"] == "true"


def test_wazuh_database_declaration_preserves_tls_and_indexer_not_api_accounts():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "wazuh"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert components == [{
        "id": "indexer", "providers": [{"type": "internal", "service": "wazuh.indexer", "driver": "opensearch"}],
        "users": [
            {"user": "${INDEXER_USERNAME}", "password": "${INDEXER_PASSWORD}", "usage": ["application", "administration"]},
            {"user": "${DASHBOARD_USERNAME}", "password": "${DASHBOARD_PASSWORD}", "usage": ["application"]},
        ],
    }]
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    indexer = compose["services"]["wazuh.indexer"]
    assert indexer["env_file"] == ".env"
    assert "./src/wazuh.indexer.yml:/usr/share/wazuh-indexer/config/opensearch.yml" in indexer["volumes"]
    assert "./src/internal_users.yml:/usr/share/wazuh-indexer/config/opensearch-security/internal_users.yml" in indexer["volumes"]
    configuration = yaml.safe_load((target / "src" / "wazuh.indexer.yml").read_text(encoding="utf-8"))
    assert configuration["plugins.security.ssl.http.enabled"] is True
    dashboard = yaml.safe_load((target / "src" / "opensearch_dashboards.yml").read_text(encoding="utf-8"))
    values = dotenv_values(target / ".env", interpolate=False)
    assert dashboard["opensearch.hosts"] == values["INDEXER_URL"] == "https://wazuh.indexer:9200"
    accounts = yaml.safe_load((target / "src" / "internal_users.yml").read_text(encoding="utf-8"))
    for user_key, password_key in [("INDEXER_USERNAME", "INDEXER_PASSWORD"), ("DASHBOARD_USERNAME", "DASHBOARD_PASSWORD")]:
        assert accounts[values[user_key]]["hash"]
        assert values[password_key]
    assert values["API_USERNAME"] not in {values["INDEXER_USERNAME"], values["DASHBOARD_USERNAME"]}
    dictionary = json.loads((REPO_ROOT / "metadata" / "database-types.json").read_text(encoding="utf-8"))
    assert dictionary["opensearch"]["port"] == 9200
    assert dictionary["opensearch"]["url"] == "https://${host}:${port}"
    assert "wazuh/wazuh-indexer" in dictionary["opensearch"]["images"]


def test_librechat_database_declaration_excludes_admin_panel_and_api_key_credentials():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "librechat"
    document, search, vector = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert document == {
        "id": "mongodb", "providers": [
            {"type": "internal", "service": "mongodb", "driver": "mongodb"},
        ],
        "name": ["LibreChat"], "users": [],
    }
    assert search == {
        "id": "meilisearch", "providers": [{"type": "internal", "service": "meilisearch", "driver": "meilisearch"}],
        "users": [],
    }
    assert vector == {
        "id": "postgres", "providers": [
            {"type": "internal", "service": "vectordb", "driver": "postgresql"},
        ],
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert services["mongodb"]["command"] == "mongod --noauth"
    assert "MONGO_URI=mongodb://${W9_ID}-mongodb:27017/LibreChat" in services["api"]["environment"]
    assert "MEILI_HOST=http://${W9_ID}-meilisearch:7700" in services["api"]["environment"]
    assert "MEILI_MASTER_KEY=${MEILI_MASTER_KEY}" in services["meilisearch"]["environment"]
    assert "MEILI_HOST=http://${W9_ID}-meilisearch:7700" in services["meilisearch"]["environment"]
    assert services["meilisearch"]["env_file"] == ".env"
    assert services["vectordb"]["environment"] == {
        "POSTGRES_DB": "librechat", "POSTGRES_USER": "librechat", "POSTGRES_PASSWORD": "${W9_POWER_PASSWORD}",
    }
    assert {"DB_HOST=${W9_ID}-postgresql", "POSTGRES_DB=librechat", "POSTGRES_USER=librechat", "POSTGRES_PASSWORD=${W9_POWER_PASSWORD}"} <= set(services["rag_api"]["environment"])
    values = dotenv_values(target / ".env", interpolate=False)
    assert not {"DB_HOST", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"} & values.keys()
    assert "clickhouse" in services["admin-panel"]["image"]
    dictionary = json.loads((REPO_ROOT / "metadata" / "database-types.json").read_text(encoding="utf-8"))
    assert dictionary["meilisearch"]["port"] == 7700
    assert dictionary["meilisearch"]["users"] == []


def test_openwebui_database_declaration_preserves_optional_chroma_profile():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "openwebui"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert components == [{
        "id": "chroma", "providers": [{"type": "internal", "service": "chroma", "driver": "chroma"}], "users": [],
    }]
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    assert compose["services"]["chroma"]["profiles"] == ["chroma"]
    assert compose["services"]["ollama"]["profiles"] == ["ollama"]
    values = dotenv_values(target / ".env", interpolate=False)
    assert not values.get("COMPOSE_PROFILES")
    assert not values.get("CHROMA_HTTP_HOST")
    dictionary = json.loads((REPO_ROOT / "metadata" / "database-types.json").read_text(encoding="utf-8"))
    assert dictionary["chroma"]["port"] == 8000
    assert "chromadb/chroma" in dictionary["chroma"]["images"]


def test_akeneo_database_inputs_are_independent_of_initialization():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "akeneo"
    database, search = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert database["providers"] == [
        {"type": "internal", "service": "mysql", "driver": "mysql"},
        {"type": "external", "drivers": ["mysql"]},
    ]
    assert database["datasource"] == {
        "APP_DATABASE_HOST": "${host}", "APP_DATABASE_PORT": "${port}", "APP_DATABASE_NAME": "${name}",
        "APP_DATABASE_USER": "${users[*].user}", "APP_DATABASE_PASSWORD": "${users[*].password}",
    }
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert services["mysql"]["environment"] == {
        "MYSQL_DATABASE": "${MYSQL_DATABASE}", "MYSQL_USER": "${MYSQL_USER}",
        "MYSQL_PASSWORD": "${MYSQL_PASSWORD}", "MYSQL_ROOT_PASSWORD": "${W9_POWER_PASSWORD}",
    }
    values = dotenv_values(target / ".env", interpolate=False)
    assert values["MYSQL_DATABASE"] == values["APP_DATABASE_NAME"] == "akeneo_pim"
    assert values["MYSQL_USER"] == values["APP_DATABASE_USER"] == "akeneo_pim"
    assert values["MYSQL_PASSWORD"] == values["APP_DATABASE_PASSWORD"] == "${W9_POWER_PASSWORD}"
    for consumer in ["akeneo", "worker"]:
        for native_input in database["datasource"]:
            assert services[consumer]["environment"][native_input] == "${" + native_input + "}"
    assert search == {
        "id": "elasticsearch", "providers": [{"type": "internal", "service": "elasticsearch", "driver": "elasticsearch"}],
        "users": [],
    }
    assert services["elasticsearch"]["environment"]["xpack.security.enabled"] == "false"

    final_build = (target / "Dockerfile").read_text(encoding="utf-8").rsplit("USER root", 1)[1]
    assert "chown -R www-data:www-data /var/www/html/var" in final_build
    assert "chown -R www-data:www-data /var/www/html\n" not in final_build
    entrypoint = (target / "src" / "entrypoint.sh").read_text(encoding="utf-8")
    assert 'chown -R www-data:www-data "${APP_DIR}/var"' in entrypoint
    assert 'chown -R www-data:www-data "${APP_DIR}"' not in entrypoint


def test_jitsu_internal_database_sources_preserve_schema_not_database():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "jitsu"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert [component["id"] for component in components] == ["postgres", "mongodb", "clickhouse"]
    assert components[0]["name"] == ["postgres"]
    assert components[1]["name"] == ["admin"]
    for component, driver in zip(components[:2], ["postgresql", "mongodb"]):
        assert component["providers"] == [
            {"type": "internal", "service": component["id"], "driver": driver},
        ]
    assert all("datasource" not in component for component in components)
    assert components[2]["providers"] == [{"type": "internal", "service": "clickhouse", "driver": "clickhouse"}]
    assert all("users" not in component for component in components)
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert services["postgres"]["environment"] == {"POSTGRES_USER": "postgres", "POSTGRES_PASSWORD": "${JITSU_POSTGRES_PASSWORD}"}
    assert services["mongodb"]["environment"] == {"MONGO_INITDB_ROOT_USERNAME": "admin", "MONGO_INITDB_ROOT_PASSWORD": "${JITSU_MONGODB_PASSWORD}"}
    assert services["clickhouse"]["environment"] == {
        "CLICKHOUSE_DB": "default", "CLICKHOUSE_USER": "default", "CLICKHOUSE_PASSWORD": "${JITSU_CLICKHOUSE_PASSWORD}",
        "CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT": 1,
    }
    for consumer in ["console", "rotor"]:
        environment = services[consumer]["environment"]
        assert environment["DATABASE_URL"] == environment["APP_DATABASE_URL"] == "postgresql://postgres:${JITSU_POSTGRES_PASSWORD}@postgres:5432/postgres?schema=newjitsu"
        assert environment["MONGODB_URL"] == "mongodb://admin:${JITSU_MONGODB_PASSWORD}@mongodb:27017/admin"
        assert environment["CLICKHOUSE_URL"] == "http://clickhouse:8123/"
        assert environment["CLICKHOUSE_HOST"] == "clickhouse:8123"
        assert environment["CLICKHOUSE_USERNAME"] == environment["CLICKHOUSE_DATABASE"] == "default"
        assert environment["CLICKHOUSE_PASSWORD"] == "${JITSU_CLICKHOUSE_PASSWORD}"
        assert environment["CLICKHOUSE_SSL"] == "false"
    for consumer, prefix in [("bulker", "BULKER"), ("ingest", "INGEST")]:
        assert services[consumer]["environment"][prefix + "_CLICKHOUSE_HOST"] == "clickhouse:8123"
        assert services[consumer]["environment"][prefix + "_CLICKHOUSE_PASSWORD"] == "${JITSU_CLICKHOUSE_PASSWORD}"
        assert services[consumer]["environment"][prefix + "_CLICKHOUSE_DATABASE"] == "default"
    values = dotenv_values(target / ".env", interpolate=False)
    assert not {"DATABASE_URL", "APP_DATABASE_URL", "MONGODB_URL", "CLICKHOUSE_URL", "CLICKHOUSE_HOST", "CLICKHOUSE_USERNAME", "CLICKHOUSE_PASSWORD", "CLICKHOUSE_DATABASE"} & values.keys()
    assert values["JITSU_POSTGRES_PASSWORD"] == values["JITSU_MONGODB_PASSWORD"] == values["JITSU_CLICKHOUSE_PASSWORD"] == "${W9_POWER_PASSWORD}"


def test_budibase_database_declaration_keeps_aliases_and_litellm_storage_distinct():
    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / "budibase"
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert [component["id"] for component in components] == ["couchdb", "redis", "litellm-postgres"]
    assert components[0]["providers"] == [
        {"type": "internal", "service": "couchdb-service", "driver": "couchdb"},
    ]
    assert "datasource" not in components[0]
    assert components[1]["providers"] == [{"type": "internal", "service": "redis-service", "driver": "redis"}]
    assert "datasource" not in components[1]
    assert components[2]["providers"] == [
        {"type": "internal", "service": "litellm-db", "driver": "postgresql"},
    ]
    assert "datasource" not in components[2]
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert "COUCHDB_USER=${COUCH_DB_USER}" in services["couchdb-service"]["environment"]
    assert "COUCHDB_PASSWORD=${COUCH_DB_PASSWORD}" in services["couchdb-service"]["environment"]
    assert services["couchdb-service"]["env_file"] == services["litellm-db"]["env_file"] == ".env"
    assert services["app-service"]["environment"]["COUCH_DB_URL"] == "http://${COUCH_DB_USER}:${COUCH_DB_PASSWORD}@${W9_ID}-couchdb:5984"
    assert services["worker-service"]["environment"]["COUCH_DB_URL"] == "http://${COUCH_DB_USER}:${COUCH_DB_PASSWORD}@couchdb-service:5984"
    assert services["worker-service"]["environment"]["COUCH_DB_USERNAME"] == "${COUCH_DB_USER}"
    assert "COUCHDB_UPSTREAM_URL=http://couchdb-service:5984" in services["proxy-service"]["environment"]
    assert services["couchdb-service"]["container_name"] == "${W9_ID}-couchdb"
    assert services["redis-service"]["command"] == "redis-server --requirepass ${REDIS_PASSWORD}"
    assert "env_file" not in services["redis-service"]
    assert services["litellm-db"]["environment"] == {
        "POSTGRES_DB": "${LITELLM_DB_NAME}", "POSTGRES_USER": "${LITELLM_DB_USER}",
        "POSTGRES_PASSWORD": "${LITELLM_DB_PASSWORD}",
    }
    assert services["litellm-service"]["environment"]["DATABASE_URL"] == "postgresql://${LITELLM_DB_USER}:${LITELLM_DB_PASSWORD}@litellm-db:5432/${LITELLM_DB_NAME}"
    values = dotenv_values(target / ".env", interpolate=False)
    assert {"COUCH_DB_USER", "COUCH_DB_PASSWORD", "REDIS_PASSWORD", "LITELLM_DB_NAME", "LITELLM_DB_USER", "LITELLM_DB_PASSWORD"} <= values.keys()
    assert not {"COUCH_DB_USERNAME", "COUCH_DB_URL", "COUCHDB_UPSTREAM_URL", "DATABASE_URL"} & values.keys()


@pytest.mark.parametrize("app,service", [
    ("drupal", "mysql"),
    ("nopcommerce", "mysql"),
    ("teamcity", "teamcity-mysql"),
])
def test_install_wizard_database_declarations_do_not_invent_external_mapping(app, service):
    target = REPO_ROOT / "apps" / app
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert components == [{
        "id": "mysql",
        "providers": [{"type": "internal", "service": service, "driver": "mysql"}],
    }]
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    environment = compose["services"][service]["environment"]
    if isinstance(environment, list):
        environment = dict(entry.split("=", 1) for entry in environment)
    assert {"MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_ROOT_PASSWORD"} <= set(environment)


@pytest.mark.parametrize("app", ["django", "laravel", "nextjs", "springboot"])
def test_runtime_database_declarations_are_optional_external_inputs(app):
    import re

    from dotenv import dotenv_values

    target = REPO_ROOT / "apps" / app
    components = json.loads((target / "variables.json").read_text(encoding="utf-8"))["database"]
    assert components == [{
        "id": "rds",
        "providers": [{"type": "external", "drivers": ["postgresql", "mysql", "mariadb"]}],
        "datasource": {"DATABASE_URL": "${url}"},
    }]
    env_path = target / ".env"
    assert not dotenv_values(env_path, interpolate=False).get("DATABASE_URL")
    assert re.search(r"^#\s*DATABASE_URL\s*=", env_path.read_text(encoding="utf-8"), re.MULTILINE)
    readme = (target / "README.md").read_text(encoding="utf-8")
    data_directory = readme.split("### Data Directory", 1)[1].split("###", 1)[0]
    assert "postgres_data" not in data_directory
    compose = yaml.safe_load((target / "docker-compose.yml").read_text(encoding="utf-8"))
    assert set(compose["services"]) <= {app, "permissions"}
    service = compose["services"][app]
    env_files = service["env_file"]
    assert ".env" in ([env_files] if isinstance(env_files, str) else env_files)
    environment = service.get("environment") or {}
    if isinstance(environment, list):
        environment = dict(entry.split("=", 1) for entry in environment)
    assert environment.get("DATABASE_URL", "${DATABASE_URL}") == "${DATABASE_URL}"


def test_repository_database_declarations_match_services_and_dictionary():
    from libs.validate import _database_metadata_result

    problems = {}
    for path in sorted((REPO_ROOT / "apps").glob("*/variables.json")):
        variables = json.loads(path.read_text(encoding="utf-8"))
        if "database" not in variables:
            continue
        result = _database_metadata_result(path.parent)
        if isinstance(variables["database"], dict):
            assert result["status"] == "legacy"
        if not result["ok"]:
            problems[path.parent.name] = result["errors"]
    assert problems == {}


@pytest.mark.parametrize("native_input,reference,coupled", [
    (None, None, False),
    ("database__connection__password", "${database__connection__password}", True),
    ("database__connection__password", "$database__connection__password", True),
    ("DB_PASSWORD", "${DB_PASSWORD}", True),
    ("database__connection__password", "${W9_POWER_PASSWORD}", False),
])
def test_external_database_inputs_are_independent_of_bundled_initialization(tmp_path, native_input, reference, coupled):
    import re

    from libs.validate import ENV_REF_RE

    root = REPO_ROOT
    if reference is not None:
        root = tmp_path
        target = root / "apps" / "example"
        target.mkdir(parents=True)
        component = {
            "id": "mysql",
            "providers": [
                {"type": "internal", "service": "mysql", "driver": "mysql"},
                {"type": "external", "drivers": ["mysql"]},
            ],
            "datasource": {native_input: "${users[*].password}"},
        }
        (target / "variables.json").write_text(json.dumps({"database": [component]}), encoding="utf-8")
        compose_fixture = {"services": {"mysql": {"environment": {"MYSQL_PASSWORD": reference}}}}
        (target / "docker-compose.yml").write_text(yaml.safe_dump(compose_fixture), encoding="utf-8")
    problems = []
    for path in sorted((root / "apps").glob("*/variables.json")):
        variables = json.loads(path.read_text(encoding="utf-8"))
        components = variables.get("database", [])
        if not components or isinstance(components, dict):
            continue
        compose = yaml.safe_load((path.parent / "docker-compose.yml").read_text(encoding="utf-8"))
        for component in components:
            if not any(provider["type"] == "external" for provider in component["providers"]):
                continue
            native_inputs = set(component["datasource"])
            for provider in component["providers"]:
                if provider["type"] != "internal":
                    continue
                environment = compose["services"][provider["service"]].get("environment") or {}
                if isinstance(environment, list):
                    environment = dict(entry.split("=", 1) if "=" in entry else (entry, None) for entry in environment)
                for key, value in environment.items():
                    if native_inputs.intersection(re.findall(ENV_REF_RE.pattern, str(value), re.IGNORECASE)):
                        problems.append(f"{path.parent.name}/{provider['service']}/{key}")
    assert problems == (["example/mysql/MYSQL_PASSWORD"] if coupled else []), f"external inputs still control bundled initialization: {problems}"


def test_documented_database_examples_validate_without_migrating_apps(tmp_path):
    import re

    from libs.validate import _database_metadata_result

    spec = (REPO_ROOT / "docs" / "app-database-connection-spec.md").read_text(encoding="utf-8")
    examples = []
    for block in re.findall(r"```json\n(.*?)\n```", spec, re.DOTALL):
        value = json.loads(block)
        if "database" in value:
            examples.append(value["database"])
    assert examples
    for example_index, example in enumerate(examples):
        components = [
            {"id": f"component-{index}", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}], **component}
            for index, component in enumerate(example)
        ]
        services = {
            provider["service"]: {}
            for component in components
            for provider in component["providers"]
            if provider["type"] == "internal"
        }
        target = tmp_path / str(example_index)
        target.mkdir()
        (target / "variables.json").write_text(json.dumps({"database": components}), encoding="utf-8")
        (target / "docker-compose.yml").write_text(yaml.safe_dump({"services": services}), encoding="utf-8")
        result = _database_metadata_result(target)
        assert result["ok"], f"documented example {example_index}: {result['errors']}"


def test_secret_coverage_snapshot_is_complete_and_current():
    from libs.secret_audit import collect_secret_coverage

    actual = collect_secret_coverage(REPO_ROOT)
    stored = json.loads((REPO_ROOT / "metadata" / "secret-coverage.json").read_text(encoding="utf-8"))
    assert stored == actual
    assert actual["app_count"] == len(list((REPO_ROOT / "apps").glob("*/variables.json")))
    assert sum(actual["status_counts"].values()) == actual["app_count"]
    assert len({entry["app"] for entry in actual["apps"]}) == actual["app_count"]
    blocked = {entry["app"] for entry in actual["apps"] if entry["status"] == "blocked"}
    assert blocked == {"semaphoreui"}
    ckan = next(entry for entry in actual["apps"] if entry["app"] == "ckan")
    assert ckan["template_check"]["ok"]
    aliases = {entry["name"]: entry["classification"] for entry in ckan["candidates"]}
    assert aliases["CKAN___API_TOKEN__JWT__ENCODE__SECRET"] == "managed_reference"
    assert aliases["CKAN___API_TOKEN__JWT__DECODE__SECRET"] == "managed_reference"
    for entry in actual["apps"]:
        assert "values" not in entry
        assert all("value" not in field for field in entry["template_check"]["fields"])


def test_declared_env_secrets_exist_in_dotenv():
    from libs.drift import parse_env_file

    problems: dict[str, list[str]] = {}
    for variables_path in sorted((REPO_ROOT / "apps").glob("*/variables.json")):
        data = json.loads(variables_path.read_text(encoding="utf-8"))
        secrets = (data.get("env") or {}).get("secrets") or []
        if not secrets:
            continue
        env_path = variables_path.parent / ".env"
        env = parse_env_file(env_path) if env_path.exists() else {}
        missing = [name for name in secrets if name not in env]
        if missing:
            problems[variables_path.parent.name] = missing
    assert problems == {}, f"apps declare env.secrets missing from .env: {problems}"


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


def test_variables_schema_accepts_explicit_no_credentials():
    schema = json.loads((REPO_ROOT / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    sample = {
        "name": "demo",
        "trademark": "Demo",
        "release": True,
        "edition": [{"dist": "community", "version": ["1.0"]}],
        "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
        "credentials": {"none": True},
    }

    jsonschema.Draft202012Validator(schema).validate(sample)
