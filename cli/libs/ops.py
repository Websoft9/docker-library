from __future__ import annotations

from datetime import timedelta

import typer

from libs import aliyun_ecs, dns, http, websoft9_upgrade
from libs.output import print_output

HELP_OPTIONS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(name="libs-ops", help="docker-library make-level operations", context_settings=HELP_OPTIONS)


@app.callback()
def main_callback(
    proxy: str | None = typer.Option(None, "--proxy", help="Proxy URL for network calls, e.g. socks5h://127.0.0.1:1089"),
) -> None:
    http.normalize_proxy_env(proxy)


@app.command("websoft9-upgrade")
def websoft9_upgrade_command(
    container: str | None = typer.Option(None, "--container", help="Websoft9 container name (default: CONTAINER in .secrets/remote.env, else websoft9)"),
    tag: str = typer.Option(websoft9_upgrade.DEFAULT_TAG, "--tag", help="Image tag to set (default: dev)"),
    tag_var: str = typer.Option(websoft9_upgrade.DEFAULT_TAG_VAR, "--tag-var", help="Env variable holding the image tag"),
    compose_dir: str | None = typer.Option(None, "--compose-dir", help="Compose project directory; discovered from container labels when omitted"),
    target: str | None = typer.Option(None, "--target", help="local | remote"),
    ssh_host: str | None = typer.Option(None, "--ssh-host", help="Remote host IP or name"),
    ssh_user: str | None = typer.Option(None, "--ssh-user", help="Remote SSH user (default root)"),
    ssh_secret_path: str | None = typer.Option(None, "--ssh-secret-path", help="SSH secret path (key or password file)"),
    progress: bool = typer.Option(False, "--progress", help="Show step progress on stderr"),
    verbose: bool = typer.Option(False, "--verbose", help="Show step progress and raw subprocess output on stderr"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Upgrade the Websoft9 platform container: set its image tag, pull, and recreate it."""
    try:
        progress_writer = (lambda message: typer.echo(message, err=True)) if (progress or verbose) else None
        payload = websoft9_upgrade.upgrade(
            container=container,
            tag=tag,
            tag_var=tag_var,
            compose_dir=compose_dir,
            target=target,
            ssh_host=ssh_host,
            ssh_user=ssh_user,
            ssh_secret_path=ssh_secret_path,
            progress=progress_writer,
            verbose=verbose,
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


@app.command("dns-bind")
def dns_bind_command(
    domain: str | None = typer.Option(None, "--domain", help="Wildcard base domain, e.g. libs.websoft9.cn; defaults to DNS_DOMAIN"),
    target: str | None = typer.Option(None, "--target", help="local | remote; defaults to TARGET in .secrets/remote.env"),
    ip: str | None = typer.Option(None, "--ip", help="Explicit IPv4 value; overrides target resolution"),
    ssh_host: str | None = typer.Option(None, "--ssh-host", help="Remote host; overrides SSH_HOST in .secrets/remote.env"),
    ssh_user: str | None = typer.Option(None, "--ssh-user", help="Remote SSH user (default root)"),
    ssh_secret_path: str | None = typer.Option(None, "--ssh-secret-path", help="SSH secret path (key or password file)"),
    container: str | None = typer.Option(None, "--container", help="Websoft9 container name (default: CONTAINER in .secrets/remote.env, else websoft9)"),
    no_container: bool = typer.Option(False, "--no-container", help="Skip the optional Websoft9 container domain binding"),
    record_type: str = typer.Option(dns.DEFAULT_RECORD_TYPE, "--type", help="DNS record type"),
    ttl: int = typer.Option(dns.DEFAULT_TTL, "--ttl", help="Record TTL in seconds"),
    access_key_id: str | None = typer.Option(None, "--access-key-id", "--key-id", help="DNS key id; overrides connector/env value"),
    access_key_secret: str | None = typer.Option(None, "--access-key-secret", "--key-secret", help="DNS key secret; overrides connector/env value"),
    endpoint: str | None = typer.Option(None, "--endpoint", help="DNS API endpoint; overrides DNS_ENDPOINT"),
    env_file: str | None = typer.Option(None, "--env-file", help="DNS env file; overrides default .secrets/dns.env"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Point the wildcard record (*.<domain>) at the remote host or localhost, updating it when present.

    When the Websoft9 container is reachable it also sets its wildcard_domain config; otherwise it skips silently.
    """
    try:
        resolved_domain = dns.resolve_domain(domain, env_file)
        payload = dns.bind(
            domain=resolved_domain,
            value=dns.resolve_target_ip(target=target, ip=ip, ssh_host=ssh_host),
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            record_type=record_type,
            ttl=ttl,
            endpoint=endpoint,
            env_file=env_file,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except (ValueError, dns.DnsError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    except Exception as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)

    if not no_container:
        payload["container_config"] = dns.configure_container(
            resolved_domain,
            target=target,
            container=container,
            ssh_host=ssh_host,
            ssh_user=ssh_user,
            ssh_secret_path=ssh_secret_path,
        )
    print_output(payload, as_json)


@app.command("dns-delete")
def dns_delete_command(
    domain: str | None = typer.Option(None, "--domain", help="Wildcard base domain, e.g. libs.websoft9.cn; defaults to DNS_DOMAIN"),
    record_type: str = typer.Option(dns.DEFAULT_RECORD_TYPE, "--type", help="DNS record type"),
    access_key_id: str | None = typer.Option(None, "--access-key-id", "--key-id", help="DNS key id; overrides connector/env value"),
    access_key_secret: str | None = typer.Option(None, "--access-key-secret", "--key-secret", help="DNS key secret; overrides connector/env value"),
    endpoint: str | None = typer.Option(None, "--endpoint", help="DNS API endpoint; overrides DNS_ENDPOINT"),
    env_file: str | None = typer.Option(None, "--env-file", help="DNS env file; overrides default .secrets/dns.env"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Delete the single wildcard record (*.<domain>) managed for the domain."""
    try:
        payload = dns.delete(
            domain=dns.resolve_domain(domain, env_file),
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            record_type=record_type,
            endpoint=endpoint,
            env_file=env_file,
        )
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except (ValueError, dns.DnsError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    except Exception as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)
    print_output(payload, as_json)


def _prompt_int_range(prompt: str, *, default: int | None, minimum: int, maximum: int) -> int:
    default = minimum if default is None else default
    while True:
        raw = typer.prompt(prompt, default=default)
        try:
            value = int(str(raw).strip())
        except ValueError:
            typer.echo("Please enter an integer.", err=True)
            continue
        if value < minimum or value > maximum:
            typer.echo(f"Please enter a value between {minimum} and {maximum}.", err=True)
            continue
        return value


@app.command("create-aliyun-ecs")
def create_aliyun_ecs_command(
    disk_size: int | None = typer.Option(None, "--disk-size", help="System disk size in GiB; prompted when omitted"),
    release_in: str | None = typer.Option(None, "--release-in", help="Auto-release after this duration (e.g. 10h, 90m, 2d)"),
    release_at: str | None = typer.Option(None, "--release-at", help="Absolute auto-release time in UTC (e.g. 2026-10-13T11:19:00Z)"),
    name: str | None = typer.Option(None, "--name", help="Instance name; defaults to the config value"),
    image_id: str | None = typer.Option(None, "--image-id", help="Use a specific image instead of resolving the marketplace product"),
    config: str | None = typer.Option(None, "--config", help="Config file; defaults to ci/cloud/aliyun-ecs.json"),
    env_file: str | None = typer.Option(None, "--env-file", help="Aliyun env file; defaults to .secrets/aliyun.env"),
    assume_yes: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt"),
    wait_timeout: int = typer.Option(aliyun_ecs.DEFAULT_WAIT_TIMEOUT, "--wait-timeout", help="Seconds to wait for the public IP after creation; 0 disables waiting"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Resolve the plan and print it without creating the instance"),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Create a pay-as-you-go (spot) Aliyun ECS instance using the fixed config plus interactive disk size and release time."""
    try:
        cfg = aliyun_ecs.load_config(config)
        low, high = aliyun_ecs.disk_bounds(cfg)
        if disk_size is None:
            disk_size = _prompt_int_range(
                f"System disk size GiB ({low}-{high})",
                default=aliyun_ecs.default_disk_size(cfg),
                minimum=int(low or 1),
                maximum=int(high or 32768),
            )
        aliyun_ecs.validate_disk_size(cfg, disk_size)

        rel_low, rel_high, rel_default = aliyun_ecs.release_hours(cfg)
        auto_release = release_at
        if not auto_release:
            if release_in:
                duration = aliyun_ecs.parse_duration(release_in)
            else:
                hours = _prompt_int_range(
                    f"Auto-release after hours ({rel_low}-{rel_high})",
                    default=rel_default,
                    minimum=rel_low,
                    maximum=rel_high,
                )
                duration = timedelta(hours=hours)
            auto_release = aliyun_ecs.auto_release_iso(duration)

        key_id, key_secret = aliyun_ecs.resolve_credentials(env_file=env_file)
        image = aliyun_ecs.resolve_image(cfg, image_id=image_id, key_id=key_id, key_secret=key_secret)
        params = aliyun_ecs.build_run_instances_params(
            cfg, image, disk_size_gib=disk_size, auto_release_time=auto_release, name=name
        )

        plan = {
            "region": cfg["region"],
            "instance_name": params.get("InstanceName"),
            "instance_type": params.get("InstanceType"),
            "image_id": image.get("image_id"),
            "image_name": image.get("image_name"),
            "disk_size_gib": disk_size,
            "disk_category": params.get("SystemDisk.Category"),
            "spot_strategy": params.get("SpotStrategy"),
            "auto_release_time": auto_release,
        }

        if not assume_yes and not dry_run:
            typer.echo("Plan:")
            for key in (
                "region",
                "instance_name",
                "instance_type",
                "disk_size_gib",
                "disk_category",
                "spot_strategy",
                "auto_release_time",
            ):
                typer.echo(f"  {key}: {plan[key]}")
            typer.echo(f"  image: {plan['image_id']} ({plan['image_name'] or image.get('source')})")
            if not typer.confirm("Create this instance?"):
                typer.echo("Aborted.")
                raise typer.Exit(code=0)

        if dry_run:
            print_output({**plan, "dry_run": True}, as_json)
            return

        result = aliyun_ecs.run_instances(params, key_id or "", key_secret or "")
        connection: dict = {}
        if result.get("instance_ids") and wait_timeout > 0:
            connection = aliyun_ecs.wait_for_public_ip(
                result["instance_ids"][0],
                key_id or "",
                key_secret or "",
                cfg["region"],
                timeout=wait_timeout,
            )
        print_output({**plan, "action": "created", **result, **connection}, as_json)
        if not as_json:
            if connection.get("public_ip"):
                typer.echo(f"server public IP: {connection['public_ip']}", err=True)
            elif connection.get("pending"):
                typer.echo("warning: public IP not assigned yet; check the console shortly", err=True)
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4)
    except (ValueError, aliyun_ecs.EcsError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    except typer.Exit:
        raise
    except Exception as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)


def run() -> int | None:
    app.registered_commands.sort(key=lambda item: item.name)
    try:
        app()
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        return 4


if __name__ == "__main__":
    run()
