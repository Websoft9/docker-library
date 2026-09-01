from __future__ import annotations

import json

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from libs import app as app_ops
from libs import app_build, app_deploy, app_tests, appstore_sync, catalog, contentful, dblifecycle, drift, http, maintenance, newapp, readme, remote, validate, versions
from libs.metadata import app_dir
from libs.output import print_output


HELP_OPTIONS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(name="libs", help="docker-library automation interface", context_settings=HELP_OPTIONS)


@app.callback()
def main_callback(
    proxy: str | None = typer.Option(None, "--proxy", help="Proxy URL for network calls, e.g. socks5h://127.0.0.1:1089"),
) -> None:
    http.normalize_proxy_env(proxy)


@app.command("proxy")
def proxy_command(
    set_url: str | None = typer.Option(None, "--set", help="Save a proxy URL to local config"),
    clear: bool = typer.Option(False, "--clear", help="Remove the saved proxy"),
) -> None:
    """Show, save, or clear the proxy used when the environment has none."""
    if set_url:
        http.save_proxy(set_url)
        typer.echo(f"saved proxy: {set_url}")
        return
    if clear:
        http.clear_proxy()
        typer.echo("saved proxy removed")
        return
    current = http.detect_proxy()
    typer.echo(current or "no proxy configured")


@app.command("help")
def help_command(ctx: typer.Context) -> None:
    """Show help for libs. Same as libs --help."""
    typer.echo(ctx.parent.get_help())
    typer.echo("\nLocal by default; remote-aware commands read defaults from .secrets/remote.env (TARGET, SSH_HOST, SSH_USER, SSH_SECRET_PATH, DEPLOY_ROOT, CONTAINER). Current remote-aware commands: app-deploy, app-build, app-down, app-tests, appstore-sync, appstore-deploy.")


@app.command("list")
def list_command(
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived apps"),
    scope: str | None = typer.Option(None, "--scope", help="Filter by scope: public | internal"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """List active apps with maintenance metadata."""
    output = app_ops.collect_apps(include_archived=include_archived, scope=scope)
    if not as_json:
        active = app_ops.collect_apps(include_archived=False)
        all_apps = app_ops.collect_apps(include_archived=True)
        internal = sum(1 for item in active if item["scope"] == "internal")
        public = len(active) - internal
        archived = len(all_apps) - len(active)
        Console().print(
            f"[dim]total {len(all_apps)} | active {len(active)} (public {public}, internal {internal}) | archived {archived}[/dim]"
        )
        if not include_archived:
            Console().print("[dim]use --include-archived to show archived apps[/dim]")
        table = Table("name", "status", "cadence", "update policy", "scope", header_style="dim", box=box.SIMPLE)
        for item in output:
            table.add_row(item["name"], item["status"], item["cadence"], item["update_policy"], item["scope"])
        Console().print(table)
        return
    print_output(output, as_json)


@app.command("app-info")
def info_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Show one app's details and maintenance metadata."""
    try:
        payload = app_ops.collect_app_info(app_name)
    except FileNotFoundError:
        raise typer.Exit(code=4)
    print_output(payload, as_json)


@app.command(
    "scan",
    epilog=(
        "Examples:\n"
        "  libs scan --selection due --plan-only\n"
        "  libs scan --app wordpress\n"
        "  libs scan --app wordpress --major-ahead 5 --json"
    ),
)
def scan_command(
    selection: str = typer.Option("all-active", help="all-active | due | weekly | monthly | quarterly"),
    target_date: str | None = typer.Option(None, "--date", help="Date used for cadence selection in YYYY-MM-DD format"),
    plan_only: bool = typer.Option(False, help="Only list selected apps without remote version checks"),
    page_size: int = typer.Option(100, help="Number of tags per Docker Hub page"),
    major_ahead: int = typer.Option(3, help="How many future majors to probe"),
    app_name: str | None = typer.Option(None, "--app", help="Scan only this app"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Scan upstream versions for selected apps."""
    payload = versions.scan_apps(
        selection=selection,
        target_date=target_date,
        plan_only=plan_only,
        page_size=page_size,
        major_ahead=major_ahead,
        app_filter=app_name,
    )
    print_output(payload, as_json)


@app.command("app-check")
def check_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    gate: str = typer.Option("all", "--gate", help="all | structure | policy"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Run quality gate checks for one app."""
    payload = validate.check_app(app_name, gate=gate)
    print_output(payload, as_json)
    if not payload["ok"]:
        raise typer.Exit(code=1)


@app.command("app-report")
def report_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Generate a short readiness report for owner E2E."""
    check = validate.check_app(app_name, gate="all")
    payload = {
        "app": app_name,
        "decision": "ready-for-e2e" if check["ok"] else "blocked",
        "automated_checks": {
            "structure": check["structure"],
            "policy": check["policy"],
        },
        "owner_e2e_focus": [],
    }
    print_output(payload, as_json)
    if payload["decision"] != "ready-for-e2e":
        raise typer.Exit(code=1)


@app.command("app-archive")
def archive_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    reason: str = typer.Option("owner-retired", help="Archive reason"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview archive actions"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Archive one app out of active maintenance."""
    try:
        payload = app_ops.archive_app(app_name, reason=reason, dry_run=dry_run)
    except FileNotFoundError:
        raise typer.Exit(code=4)
    print_output(payload, as_json)


@app.command("app-restore")
def restore_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    cadence: str = typer.Option("monthly", help="Maintenance cadence after restore"),
    update_policy: str = typer.Option("patch-minor", help="Update policy after restore"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview restore actions"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Restore one archived app back to active maintenance."""
    try:
        payload = app_ops.restore_app(app_name, cadence=cadence, update_policy=update_policy, dry_run=dry_run)
    except FileNotFoundError:
        raise typer.Exit(code=4)
    except FileExistsError:
        raise typer.BadParameter(f"apps/{app_name} already exists; use app-update instead")
    print_output(payload, as_json)


@app.command("app-drift")
def drift_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """List dependency images and compare upstream compose drift."""
    target = app_dir(app_name)
    if not target:
        raise typer.Exit(code=4)

    compose_path = target / "docker-compose.yml"
    if not compose_path.exists():
        raise typer.Exit(code=4)

    compose = drift.parse_compose(compose_path)
    payload = {
        "app": app_name,
        "dependency_images": drift.dependency_images(compose),
        "compose_source": {
            "declared": False,
            "type": None,
            "url": None,
        },
        "config_source": {
            "declared": False,
            "type": None,
            "url": None,
        },
        "compose_drift": {
            "status": "not-declared",
            "diff": None,
            "error": None,
        },
        "config_drift": {
            "status": "not-declared",
            "diff": None,
            "error": None,
        },
    }

    variables_path = target / "variables.json"
    if variables_path.exists():
        variables = json.loads(variables_path.read_text(encoding="utf-8"))
        upstream = variables.get("upstream") or {}
        compose_group = upstream.get("compose") or {}
        compose_url = compose_group.get("compose")
        compose_source = {"type": "raw-compose", "url": compose_url} if compose_url else (upstream.get("compose_source") or {})
        config_url = compose_group.get("env")
        config_source = {"type": "raw-env", "url": config_url} if config_url else (upstream.get("config_source") or {})
        payload["compose_source"] = {
            "declared": bool(compose_source.get("type") and compose_source.get("url")),
            "type": compose_source.get("type"),
            "url": compose_source.get("url"),
        }
        payload["config_source"] = {
            "declared": bool(config_source.get("type") and config_source.get("url")),
            "type": config_source.get("type"),
            "url": config_source.get("url"),
        }
        if compose_source.get("type") == "raw-compose" and compose_source.get("url"):
            upstream_compose, error = drift.fetch_upstream_compose(compose_source["url"])
            if error:
                payload["compose_drift"] = {
                    "status": "source-error",
                    "diff": None,
                    "error": error,
                }
            else:
                payload["compose_drift"] = {
                    "status": "ok",
                    "diff": drift.diff_services(compose, upstream_compose),
                    "error": None,
                }

        if config_source.get("type") in ("raw-env", "raw-yaml") and config_source.get("url"):
            upstream_text, error = drift.fetch_upstream_text(config_source["url"])
            if error:
                payload["config_drift"] = {
                    "status": "source-error",
                    "diff": None,
                    "error": error,
                }
            else:
                local_env = drift.parse_env_file(target / ".env")
                upstream_env = drift.parse_env_text(upstream_text)
                payload["config_drift"] = {
                    "status": "ok",
                    "diff": drift.diff_config(local_env, upstream_env),
                    "error": None,
                }

    print_output(payload, as_json)


@app.command("db-refresh")
def db_refresh_command(
    engine: str | None = typer.Option(None, "--engine", help="Refresh only one engine"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Refresh the DB lifecycle snapshot from endoflife.date."""
    try:
        payload = dblifecycle.refresh_lifecycle(engine=engine)
    except ValueError as error:
        raise typer.BadParameter(str(error))
    except Exception as error:
        typer.echo(f"refresh failed: {error}", err=True)
        raise typer.Exit(code=1)
    print_output(payload, as_json)


@app.command("maintenance-check")
def check_maintenance_command() -> None:
    """Validate maintenance/archive metadata against the app tree."""
    try:
        maintenance.load_maintenance_metadata()
    except Exception as error:
        typer.echo(f"maintenance metadata invalid: {error}", err=True)
        raise typer.Exit(code=1)
    typer.echo("maintenance metadata valid")


@app.command("app-new")
def new_app_command(
    name: str = typer.Option(..., "--name", help="App name, lowercase directory name"),
    trademark: str = typer.Option(..., "--trademark", help="Brand display name, e.g. WordPress"),
    version: str | None = typer.Option(None, "--version", help="Image version, e.g. 7.0; TODO placeholder when omitted"),
    repo: str | None = typer.Option(None, "--repo", help="Image reference, e.g. wordpress or ghcr.io/ns/img; TODO placeholder when omitted"),
    docs_github: str | None = typer.Option(None, "--docs-github", help="Project repository URL"),
    docs_image: str | None = typer.Option(None, "--docs-image", help="Official image registry URL"),
    docs_install: str | None = typer.Option(None, "--docs-install", help="Official install reference URL"),
    upstream_releases: str | None = typer.Option(None, "--upstream-releases", help="Project releases or tags URL"),
    upstream_compose: str | None = typer.Option(None, "--upstream-compose", help="Official compose file URL"),
    upstream_env: str | None = typer.Option(None, "--upstream-env", help="Official env example URL"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview files without writing"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Validate a new app request and scaffold the app package skeleton."""
    docs = {}
    for key, value in (("github", docs_github), ("image", docs_image), ("install", docs_install)):
        if value:
            docs[key] = value
    upstream = {}
    for key, value in (("releases", upstream_releases), ("compose", upstream_compose), ("env", upstream_env)):
        if value:
            upstream[key] = value

    try:
        payload = newapp.scaffold(
            name=name,
            trademark=trademark,
            version=version or "",
            repo=repo or "",
            docs=docs,
            upstream=upstream,
            dry_run=dry_run,
        )
    except ValueError as error:
        raise typer.BadParameter(str(error))
    except FileExistsError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    print_output(payload, as_json)


@app.command("app-gen-readme")
def gen_readme_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Generate one app's README.md from variables.json."""
    try:
        payload = readme.render_readme(app_name)
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    print_output(payload, as_json)


@app.command("catalog-refresh")
def catalog_refresh_command(
    url: str = typer.Option(catalog.DEFAULT_CATALOG_URL, "--url", help="Published catalog artifact URL"),
    output: str = typer.Option(catalog.DEFAULT_TAXONOMY_OUTPUT, "--output", help="Repo-relative taxonomy snapshot path"),
    check_product_schema: bool = typer.Option(False, "--check-product-schema", help="Also validate the published product artifact shape"),
    product_url: str = typer.Option(catalog.DEFAULT_PRODUCT_URL, "--product-url", help="Published product artifact URL used by --check-product-schema"),
    apply: bool = typer.Option(False, "--apply", help="Write the snapshot instead of previewing"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Refresh the repo catalog taxonomy snapshot from a published catalog artifact."""
    try:
        payload = catalog.refresh_catalog(
            url=url,
            output=output,
            apply=apply,
            check_product_schema=check_product_schema,
            product_url=product_url,
        )
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    print_output(payload, as_json)


@app.command("catalog-pull")
def catalog_pull_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    product_url: str = typer.Option(catalog.DEFAULT_PRODUCT_URL, "--product-url", help="Published product artifact URL"),
    catalog_dir: str = typer.Option(catalog.DEFAULT_CATALOG_DIR, "--catalog-dir", help="Repo catalog directory"),
    only_diff: bool = typer.Option(False, "--only-diff", help="Show differences only; do not include incoming payload"),
    apply: bool = typer.Option(False, "--apply", help="Write the pulled catalog data instead of previewing"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Pull one app's published commercial data into metadata/catalog, or show a diff only."""
    try:
        payload = catalog.pull_catalog(
            app_name=app_name,
            product_url=product_url,
            catalog_dir=catalog_dir,
            apply=apply,
            only_diff=only_diff,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    print_output(payload, as_json)


@app.command("catalog-push")
def catalog_push_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    environment: str = typer.Option("master", "--environment", help="Contentful environment"),
    catalog_dir: str = typer.Option(catalog.DEFAULT_CATALOG_DIR, "--catalog-dir", help="Repo catalog directory"),
    token: str | None = typer.Option(None, "--token", help="Contentful access token; highest-priority override"),
    env_file: str | None = typer.Option(None, "--env-file", help="Contentful env file; overrides default .secrets/contentful.env"),
    apply: bool = typer.Option(False, "--apply", help="Write to Contentful instead of previewing"),
    update_machine: bool = typer.Option(False, "--update-machine", help="When the entry exists, refresh machine fields only"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Push one app's repo catalog data and machine fields to Contentful; previews by default."""
    try:
        payload = contentful.sync_app(
            app_name=app_name,
            environment=environment,
            drafts_dir=catalog_dir,
            apply=apply,
            update_machine=update_machine,
            token=token,
            env_file=env_file,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    print_output(payload, as_json)


@app.command("catalog-update")
def catalog_update_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    fields_json: str = typer.Option(
        ...,
        "--fields",
        help='JSON object of fields to update, e.g. \'{"appStore": false, "production": false}\'',
    ),
    environment: str = typer.Option("master", "--environment", help="Contentful environment"),
    token: str | None = typer.Option(None, "--token", help="Contentful access token; highest-priority override"),
    env_file: str | None = typer.Option(None, "--env-file", help="Contentful env file; overrides default .secrets/contentful.env"),
    apply: bool = typer.Option(False, "--apply", help="Write to Contentful instead of previewing"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Update fields on an existing catalog/product entry in Contentful; previews by default."""
    try:
        fields = json.loads(fields_json)
        if not isinstance(fields, dict):
            raise ValueError("--fields must be a JSON object")
    except json.JSONDecodeError as error:
        typer.echo(f"invalid --fields JSON: {error}", err=True)
        raise typer.Exit(code=2)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    try:
        payload = contentful.update_fields(
            app_name=app_name,
            environment=environment,
            fields=fields,
            apply=apply,
            token=token,
            env_file=env_file,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    print_output(payload, as_json)


@app.command("appstore-sync")
def appstore_sync_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    ssh_host: str | None = typer.Option(None, "--ssh-host", help="Remote host IP or name"),
    ssh_user: str | None = typer.Option(None, "--ssh-user", help="Remote SSH user (default root)"),
    ssh_secret_path: str | None = typer.Option(None, "--ssh-secret-path", help="SSH secret path (key or password file)"),
    container: str | None = typer.Option(None, "--container", help="Remote websoft9 container name (default: CONTAINER in .secrets/remote.env, else websoft9)"),
    json_dir: str = typer.Option(appstore_sync.DEFAULT_JSON_DIR, "--json-dir", help="JSON directory inside the container"),
    progress: bool = typer.Option(False, "--progress", help="Show step progress on stderr"),
    verbose: bool = typer.Option(False, "--verbose", help="Show step progress and raw subprocess output on stderr"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Sync one app into the remote websoft9 appstore JSON preview and app directory."""
    try:
        progress_writer = (lambda message: typer.echo(message, err=True)) if (progress or verbose) else None
        payload = appstore_sync.prepare_preview(
            app_name=app_name,
            host=ssh_host,
            user=ssh_user,
            secret_path=ssh_secret_path,
            container=container,
            json_dir=json_dir,
            progress=progress_writer,
            verbose=verbose,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except Exception as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)
    print_output(payload, as_json)


@app.command("app-deploy")
def app_deploy_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    target: str | None = typer.Option(None, "--target", help="local | remote"),
    ssh_host: str | None = typer.Option(None, "--ssh-host", help="Remote host IP or name"),
    ssh_user: str | None = typer.Option(None, "--ssh-user", help="Remote SSH user (default root)"),
    ssh_secret_path: str | None = typer.Option(None, "--ssh-secret-path", help="SSH secret path (key or password file)"),
    deploy_root: str | None = typer.Option(None, "--deploy-root", help="Remote deploy root"),
    version: str | None = typer.Option(None, "--version", help="Deploy a specific image tag by overriding W9_VERSION; repo .env is not modified"),
    down: bool = typer.Option(False, "--down", help="Tear the app down with docker compose down -v instead of up -d"),
    progress: bool = typer.Option(False, "--progress", help="Show step progress on stderr"),
    verbose: bool = typer.Option(False, "--verbose", help="Show step progress and raw subprocess output on stderr"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Run docker compose deploy/teardown for one app."""
    try:
        progress_writer = (lambda message: typer.echo(message, err=True)) if (progress or verbose) else None
        payload = app_deploy.deploy(
            app_name=app_name,
            target=target,
            ssh_host=ssh_host,
            ssh_user=ssh_user,
            ssh_secret_path=ssh_secret_path,
            deploy_root=deploy_root,
            version=version,
            down=down,
            progress=progress_writer,
            verbose=verbose,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except Exception as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)
    print_output(payload, as_json)


@app.command("app-build")
def app_build_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    push: bool = typer.Option(False, "--push", help="Push built image tags after a successful build"),
    registry: str | None = typer.Option(None, "--registry", help="Optional registry hostname for docker login"),
    username: str | None = typer.Option(None, "--username", help="Registry username; overrides connector/env value"),
    password: str | None = typer.Option(None, "--password", help="Registry password; overrides connector/env value"),
    token: str | None = typer.Option(None, "--token", help="Registry token; highest-priority secret override"),
    env_file: str | None = typer.Option(None, "--env-file", help="Docker Hub env file; overrides default .secrets/dockerhub.env"),
    progress: bool = typer.Option(False, "--progress", help="Show build/push progress on stderr"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Build one app's Dockerfile-backed services, and optionally push tagged images."""
    try:
        payload = app_build.build_app(
            app_name=app_name,
            push=push,
            env_file=env_file,
            username=username,
            password=password,
            token=token,
            registry=registry,
            progress=(lambda message: typer.echo(message, err=True)) if progress else None,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    except Exception as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)
    print_output(payload, as_json)


@app.command("app-down")
def app_down_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    target: str | None = typer.Option(None, "--target", help="local | remote"),
    ssh_host: str | None = typer.Option(None, "--ssh-host", help="Remote host IP or name"),
    ssh_user: str | None = typer.Option(None, "--ssh-user", help="Remote SSH user (default root)"),
    ssh_secret_path: str | None = typer.Option(None, "--ssh-secret-path", help="SSH secret path (key or password file)"),
    deploy_root: str | None = typer.Option(None, "--deploy-root", help="Remote deploy root"),
    progress: bool = typer.Option(False, "--progress", help="Show step progress on stderr"),
    verbose: bool = typer.Option(False, "--verbose", help="Show step progress and raw subprocess output on stderr"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Tear one app down with docker compose down -v."""
    try:
        progress_writer = (lambda message: typer.echo(message, err=True)) if (progress or verbose) else None
        payload = app_deploy.deploy(
            app_name=app_name,
            target=target,
            ssh_host=ssh_host,
            ssh_user=ssh_user,
            ssh_secret_path=ssh_secret_path,
            deploy_root=deploy_root,
            down=True,
            progress=progress_writer,
            verbose=verbose,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except Exception as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)
    print_output(payload, as_json)


@app.command("appstore-deploy")
def appstore_deploy_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    ssh_host: str | None = typer.Option(None, "--ssh-host", help="Remote host IP or name"),
    ssh_user: str | None = typer.Option(None, "--ssh-user", help="Remote SSH user (default root)"),
    ssh_secret_path: str | None = typer.Option(None, "--ssh-secret-path", help="SSH secret path (key or password file)"),
    deploy_root: str | None = typer.Option(None, "--deploy-root", help="Remote appstore root"),
    progress: bool = typer.Option(False, "--progress", help="Show step progress on stderr"),
    verbose: bool = typer.Option(False, "--verbose", help="Show step progress and raw subprocess output on stderr"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Deploy one app into a websoft9 container appstore. Not implemented yet; pending the websoft9 container CLI."""
    if progress or verbose:
        typer.echo("[1/1] appstore-deploy is not implemented yet", err=True)
    typer.echo(
        f"appstore-deploy is not implemented yet; it will be added when the websoft9 container provides the corresponding CLI (app: {app_name}, deploy_root: {deploy_root or '/websoft9/library/apps'}).",
        err=True,
    )
    raise typer.Exit(code=1)


@app.command("app-tests")
def app_tests_command(
    app_name: str = typer.Option(..., "--app", help="App name"),
    base_url: str | None = typer.Option(None, "--base-url", help="Override the base URL used by web checks"),
    ssh_host: str | None = typer.Option(None, "--ssh-host", help="Remote host IP or name"),
    ssh_user: str | None = typer.Option(None, "--ssh-user", help="Remote SSH user (default root)"),
    ssh_secret_path: str | None = typer.Option(None, "--ssh-secret-path", help="SSH secret path (key or password file)"),
    deploy_root: str | None = typer.Option(None, "--deploy-root", help="Remote deploy root"),
    wait_timeout: int = typer.Option(60, "--wait-timeout", min=0, help="Total seconds to wait/retry readiness checks"),
    wait_interval: int = typer.Option(5, "--wait-interval", min=1, help="Seconds between readiness retries"),
    progress: bool = typer.Option(False, "--progress", help="Show step progress on stderr"),
    verbose: bool = typer.Option(False, "--verbose", help="Show step progress and raw subprocess output on stderr"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Run app functional checks declared in apps/<app>/tests/cases.yml."""
    try:
        payload = app_tests.run_app_tests(
            app_name,
            base_url=base_url,
            ssh_host=ssh_host,
            ssh_user=ssh_user,
            ssh_secret_path=ssh_secret_path,
            deploy_root=deploy_root,
            wait_timeout=wait_timeout,
            wait_interval=wait_interval,
            progress=(lambda message: typer.echo(message, err=True)) if (progress or verbose) else None,
            verbose=verbose,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    print_output(payload, as_json)
    if not payload["ok"]:
        raise typer.Exit(code=1)


def run() -> int | None:
    app.registered_commands.sort(key=lambda item: item.name)
    try:
        app()
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        return 4
