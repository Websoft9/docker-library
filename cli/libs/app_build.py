from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import yaml

from libs import remote
from libs.credentials import resolve_secret
from libs.metadata import app_dir
from libs.repo import repo_path


DOCKERHUB_USER_ENV = "DOCKERHUB_USERNAME"
DOCKERHUB_PASSWORD_ENV = "DOCKERHUB_PASSWORD"
DOCKERHUB_TOKEN_ENV = "DOCKERHUB_TOKEN"


def _env_map(target: Path) -> dict[str, str]:
    env_path = target / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _load_compose(app_name: str) -> tuple[Path, dict]:
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)
    compose_path = target / "docker-compose.yml"
    if not compose_path.exists():
        raise FileNotFoundError(compose_path)
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
    return target, compose


def _env_value(target: Path, key: str) -> str | None:
    return _env_map(target).get(key)


def _build_services(compose: dict) -> list[str]:
    services = compose.get("services") or {}
    return [name for name, service in services.items() if isinstance(service, dict) and service.get("build")]


def _resolve_image_template(image: str, env: dict[str, str]) -> str:
    def repl(match: re.Match) -> str:
        key = match.group(1) or match.group(2)
        return env.get(key, match.group(0))

    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)", repl, image)


def _tagged_images(target: Path, compose: dict, services: list[str]) -> list[str]:
    all_services = compose.get("services") or {}
    env = _env_map(target)
    images: list[str] = []
    for name in services:
        service = all_services.get(name) or {}
        image = service.get("image")
        if isinstance(image, str) and image not in images:
            images.append(_resolve_image_template(image, env))
    return images


def _stable_image_tags(images: list[str]) -> list[str]:
    stable = []
    for image in images:
        if ":" not in image:
            stable.append(image)
            continue
        tag = image.rsplit(":", 1)[1]
        if tag.startswith("dev-") or tag == "dev-latest":
            continue
        stable.append(image)
    return stable


def can_build(app_name: str) -> bool:
    """True when this app needs a local/remote image build before compose up.

    True if compose declares build services, or a root Dockerfile declares the
    version ARG (pull-only custom image). False for pure official-image apps.
    """
    try:
        _, compose = _load_compose(app_name)
    except FileNotFoundError:
        return False
    if _build_services(compose):
        return True
    try:
        _dockerfile_plan(app_name)
        return True
    except ValueError:
        return False


def build_image_refs(app_name: str) -> list[str]:
    """Images that would be produced by a local build of this app."""
    try:
        source, compose = _load_compose(app_name)
    except FileNotFoundError:
        return []
    services = _build_services(compose)
    if services:
        return _tagged_images(source, compose, services)
    try:
        return _dockerfile_plan(app_name)["images"]
    except ValueError:
        return []


def resolve_image(app_name: str, image: str) -> str:
    """Resolve env placeholders in a compose image reference using the app .env."""
    target = app_dir(app_name)
    if not target:
        return image
    return _resolve_image_template(image, _env_map(target))


def _dockerfile_plan(app_name: str) -> dict:
    """Plan a direct Dockerfile build (pull-only app). Per docs/image-tag-spec.md.

    Returns {version_arg, w9_version, images}; build must run with CWD = app dir.
    """
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)
    dockerfile = target / "Dockerfile"
    if not dockerfile.exists():
        raise ValueError(f"app {app_name} has neither compose build services nor a root Dockerfile")
    app_upper = app_name.upper()
    version_arg = f"{app_upper}_VERSION"
    if not re.search(rf"^ARG\s+{re.escape(version_arg)}=", dockerfile.read_text(encoding="utf-8"), re.M):
        raise ValueError(
            f"app {app_name} Dockerfile does not declare ARG {version_arg}=; "
            "add it (see docs/image-tag-spec.md) or build manually"
        )
    w9_version = _env_value(target, "W9_VERSION")
    w9_repo = _env_value(target, "W9_REPO")
    if not w9_version:
        raise ValueError(f"app {app_name} W9_VERSION missing in .env")
    if not w9_repo:
        raise ValueError(f"app {app_name} W9_REPO missing in .env")
    return {
        "version_arg": version_arg,
        "w9_version": w9_version,
        "w9_repo": w9_repo,
        "images": [f"{w9_repo}:{w9_version}"],
    }


def build_plan(app_name: str, channel: str = "stable", git_sha: str | None = None) -> dict:
    """Return the canonical image build/tag plan for one app.

    This is the shared rules entrypoint for CI and controlled manual push.
    """
    source, compose = _load_compose(app_name)
    plan = _dockerfile_plan(app_name)
    channel = (channel or "stable").strip().lower()
    version = plan["w9_version"]
    repo = plan["w9_repo"]
    if channel not in {"stable", "dev"}:
        raise ValueError(f"unsupported channel: {channel}")

    if channel == "dev":
        resolved_sha = (git_sha or "").strip() or None
        if not resolved_sha:
            resolved_sha = None
        if not resolved_sha:
            raise ValueError("git_sha is required for dev channel")
        short_sha = resolved_sha[:7]
        tags = [f"{repo}:dev-{short_sha}", f"{repo}:dev-latest"]
    else:
        if "-" in version:
            tags = [f"{repo}:{version}"]
        else:
            tags = [f"{repo}:latest"]
            part = ""
            for index, fragment in enumerate(version.split(".")):
                if index == 0:
                    part = fragment
                else:
                    part = f"{part}.{fragment}"
                tags.append(f"{repo}:{part}")

    return {
        "app": app_name,
        "channel": channel,
        "context": str(source.relative_to(repo_path())),
        "dockerfile": str((source / "Dockerfile").relative_to(repo_path())),
        "build_type": "dockerfile" if not _build_services(compose) else "compose",
        "build_services": _build_services(compose),
        "version_arg": plan["version_arg"],
        "w9_version": version,
        "w9_repo": repo,
        "tags": tags,
        "primary_image": tags[0],
        "source_path": str(source.relative_to(repo_path())),
    }


def _run_stream(command: list[str], progress=None) -> subprocess.CompletedProcess:
    return remote.stream_command(command, on_line=progress)


def _sync_app_dir(
    app_name: str,
    host: str,
    user: str,
    secret_path: Path,
    deploy_root: str,
    progress=None,
) -> None:
    prepare = remote.stream_ssh(
        host,
        user,
        secret_path,
        f"mkdir -p {deploy_root} && rm -rf {deploy_root}/{app_name}",
        on_line=progress,
    )
    if prepare.returncode != 0:
        raise RuntimeError(prepare.stderr.strip() or prepare.stdout.strip() or "remote prepare failed")
    copy = remote.run_command(
        remote.scp_base(host, user, secret_path) + ["-r", str(repo_path("apps", app_name)), f"{user}@{host}:{deploy_root}/"]
    )
    if copy.returncode != 0:
        raise RuntimeError(copy.stderr.strip() or copy.stdout.strip() or "remote sync failed")


def _docker_login(registry: str | None, username: str, password: str, progress=None) -> None:
    command = ["docker", "login"]
    if registry:
        command.append(registry)
    command.extend(["-u", username, "--password-stdin"])
    process = subprocess.run(command, input=password, text=True, capture_output=True, check=False)
    if progress and process.stdout.strip():
        progress(process.stdout.strip())
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "docker login failed")


def _docker_login_remote(host: str, user: str, secret_path: Path, registry: str | None, username: str, password: str, progress=None) -> None:
    login_cmd = "docker login"
    if registry:
        login_cmd += f" {registry}"
    login_cmd += f" -u {username} --password-stdin"
    process = subprocess.run(
        remote.ssh_base(host, user, secret_path) + [login_cmd],
        input=password,
        text=True,
        capture_output=True,
        check=False,
    )
    if progress and process.stdout.strip():
        progress(process.stdout.strip())
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "remote docker login failed")


def _resolve_dockerhub_credentials(env_file: str | None, username: str | None, password: str | None, token: str | None) -> tuple[str, str]:
    login_password = token or password or resolve_secret(DOCKERHUB_TOKEN_ENV, "dockerhub", env_file=env_file) or resolve_secret(DOCKERHUB_PASSWORD_ENV, "dockerhub", env_file=env_file)
    login_username = username or resolve_secret(DOCKERHUB_USER_ENV, "dockerhub", env_file=env_file)
    if not login_username or not login_password:
        raise FileNotFoundError(
            "missing Docker Hub credentials; set DOCKERHUB_USERNAME and DOCKERHUB_PASSWORD or DOCKERHUB_TOKEN in env or .secrets/dockerhub.env"
        )
    return login_username, login_password


def build_app(
    app_name: str,
    push: bool = False,
    confirm_stable: bool = False,
    target: str | None = None,
    ssh_host: str | None = None,
    ssh_user: str | None = None,
    ssh_secret_path: str | None = None,
    deploy_root: str | None = None,
    env_file: str | None = None,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    registry: str | None = None,
    skip_sync: bool = False,
    compose_env_file: str | None = None,
    progress=None,
) -> dict:
    source, compose = _load_compose(app_name)
    build_services = _build_services(compose)

    if build_services:
        images = _tagged_images(source, compose, build_services)
        build_services_out = build_services
    else:
        plan = _dockerfile_plan(app_name)
        images = plan["images"]
        build_services_out = []

    if push and not images:
        raise ValueError(f"app {app_name} build services have no image tags to push")

    if push and not confirm_stable and not os.getenv("GITHUB_ACTIONS"):
        stable = _stable_image_tags(images)
        if stable:
            raise ValueError(
                "refusing to push stable tags outside CI without --confirm-stable; "
                f"stable targets: {', '.join(stable)}"
            )

    if target:
        mode = target
    elif ssh_host:
        mode = "remote"
    else:
        mode = remote.default_target()

    if mode == "local":
        if build_services:
            build_command = [
                "docker",
                "compose",
                "--progress",
                "plain",
                "-f",
                str(source / "docker-compose.yml"),
                "--env-file",
                str(compose_env_file if compose_env_file else source / ".env"),
                "build",
                *build_services,
            ]
        else:
            build_command = [
                "docker",
                "build",
                "-f",
                str(source / "Dockerfile"),
                "--build-arg",
                f"{plan['version_arg']}={plan['w9_version']}",
                "-t",
                images[0],
                str(source),
            ]
        build_result = _run_stream(build_command, progress=progress)
        if build_result.returncode != 0:
            raise RuntimeError(build_result.stdout.strip() or "docker build failed")

        pushed: list[str] = []
        if push:
            login_username, login_password = _resolve_dockerhub_credentials(env_file, username, password, token)
            _docker_login(registry, login_username, login_password, progress=progress)
            for image in images:
                result = _run_stream(["docker", "push", image], progress=progress)
                if result.returncode != 0:
                    raise RuntimeError(result.stdout.strip() or f"docker push failed for {image}")
                pushed.append(image)

        return {
            "app": app_name,
            "target": "local",
            "build_services": build_services_out,
            "images": images,
            "pushed": pushed,
            "push": push,
            "path": str(source.relative_to(repo_path())),
        }

    host = remote.ssh_host(ssh_host)
    if not host:
        raise FileNotFoundError("missing SSH host; pass --ssh-host or set SSH_HOST in .secrets/remote.env")
    user = remote.ssh_user(ssh_user)
    secret_path = remote.resolve_secret_path(ssh_secret_path)
    if not secret_path.exists():
        raise FileNotFoundError(f"SSH secret not found: {secret_path}")
    deploy_root_value = remote.deploy_root(deploy_root)
    app_target = f"{deploy_root_value}/{app_name}"

    if not skip_sync:
        _sync_app_dir(app_name, host, user, secret_path, deploy_root_value, progress=progress)

    if build_services:
        build_script = (
            f"docker compose --progress plain -f {app_target}/docker-compose.yml "
            f"--env-file {app_target}/.env build {' '.join(build_services)}"
        )
    else:
        build_script = (
            f"cd {app_target} && docker build -f Dockerfile "
            f"--build-arg {plan['version_arg']}={plan['w9_version']} -t {images[0]} ."
        )
    build_result = remote.stream_ssh(host, user, secret_path, build_script, on_line=progress)
    if build_result.returncode != 0:
        raise RuntimeError(build_result.stdout.strip() or "remote docker build failed")

    pushed = []
    if push:
        login_username, login_password = _resolve_dockerhub_credentials(env_file, username, password, token)
        _docker_login_remote(host, user, secret_path, registry, login_username, login_password, progress=progress)
        for image in images:
            result = remote.run_command(remote.ssh_base(host, user, secret_path) + [f"docker push {image}"])
            if result.returncode != 0:
                raise RuntimeError(result.stdout.strip() or f"remote docker push failed for {image}")
            pushed.append(image)

    return {
        "app": app_name,
        "target": "remote",
        "host": host,
        "user": user,
        "ssh_secret_path": str(secret_path),
        "deploy_root": deploy_root_value,
        "app_target": app_target,
        "build_services": build_services_out,
        "images": images,
        "pushed": pushed,
        "push": push,
        "path": str(source.relative_to(repo_path())),
    }
