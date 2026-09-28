from __future__ import annotations

import os
import platform as _host
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
DOCKERHUB_ORG_ENV = "DOCKERHUB_ORG"

DEFAULT_PLATFORM = "amd64"
PLATFORM_CHOICES = {
    "amd64": "linux/amd64",
    "arm64": "linux/arm64",
    "both": "linux/amd64,linux/arm64",
}


BINFMT_HANDLERS = {"amd64": "qemu-x86_64", "arm64": "qemu-aarch64"}
BINFMT_IMAGE = "tonistiigi/binfmt"
BUILDER_HINT = (
    "the current buildx builder does not support multi-platform builds; create a container builder first: "
    "docker buildx create --name multiarch --driver docker-container --use"
)

GIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


def _promote_source_ref(source_sha: str | None) -> str:
    """Resolve the promote source tag from an optional commit SHA.

    Returns ``dev-<short-sha>`` for a validated SHA, otherwise the rolling
    ``dev-latest`` alias. Pinning the SHA keeps the promoted stable artifact
    identical to the validated candidate instead of tracking a moving alias.
    """
    candidate = (source_sha or "").strip()
    if candidate.startswith("dev-"):
        candidate = candidate[4:]
    if not candidate:
        return "dev-latest"
    if not GIT_SHA_RE.fullmatch(candidate):
        raise ValueError(f"source_sha must be a 7-40 character hex commit SHA, got: {source_sha!r}")
    return f"dev-{candidate[:7]}"


def _resolve_platform(platform: str | None) -> str | None:
    """Normalize a platform choice; None keeps the builder host-native.

    The CLI defaults to `amd64`; internal callers such as app-deploy pass None
    so a build for the target host is not forced into a cross-build.
    """
    if platform is None or not str(platform).strip():
        return None
    key = str(platform).strip().lower()
    if key not in PLATFORM_CHOICES:
        raise ValueError(f"unsupported platform: {platform} (expected amd64, arm64, or both)")
    return key


def _normalize_arch(machine: str | None) -> str | None:
    value = (machine or "").strip().lower()
    if value in {"x86_64", "amd64"}:
        return "amd64"
    if value in {"aarch64", "arm64"}:
        return "arm64"
    return None


def _local_arch() -> str | None:
    return _normalize_arch(_host.machine())


def _required_binfmt_archs(platform_key: str | None, host_arch: str | None) -> list[str]:
    """Foreign arches that need emulation on the build host."""
    if not platform_key:
        return []
    targets = ["amd64", "arm64"] if platform_key == "both" else [platform_key]
    return [arch for arch in targets if arch != host_arch]


def _ensure_binfmt_local(archs: list[str], progress=None) -> None:
    if not archs or _host.system().lower() != "linux":
        return
    for arch in archs:
        if Path(f"/proc/sys/fs/binfmt_misc/{BINFMT_HANDLERS[arch]}").exists():
            continue
        if progress:
            progress(f"installing {arch} emulation via {BINFMT_IMAGE}")
        result = subprocess.run(
            ["docker", "run", "--privileged", "--rm", BINFMT_IMAGE, "--install", arch],
            capture_output=True,
            text=True,
            check=False,
        )
        if progress and result.stdout.strip():
            progress(result.stdout.strip())
        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
                or f"failed to install {arch} emulation; run: docker run --privileged --rm {BINFMT_IMAGE} --install {arch}"
            )


def _ensure_binfmt_remote(host: str, user: str, secret_path: Path, archs: list[str], progress=None) -> None:
    if not archs:
        return
    checks = " ".join(
        f"if [ ! -e /proc/sys/fs/binfmt_misc/{BINFMT_HANDLERS[arch]} ]; then "
        f"echo installing {arch} emulation; docker run --privileged --rm {BINFMT_IMAGE} --install {arch}; fi;"
        for arch in archs
    )
    script = f'if [ "$(uname -s)" = "Linux" ]; then {checks} fi'
    result = remote.stream_ssh(host, user, secret_path, script, on_line=progress)
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or "failed to install binfmt emulation on remote host")


def _remote_arch(host: str, user: str, secret_path: Path) -> str | None:
    result = remote.run_command(remote.ssh_base(host, user, secret_path) + ["uname -m"])
    if result.returncode != 0:
        return None
    return _normalize_arch(result.stdout)


def _buildx_error(output: str) -> str:
    text = output.strip() or "docker buildx build failed"
    lowered = text.lower()
    if "multiple platforms" in lowered or "not supported for docker driver" in lowered:
        return f"{text}\n{BUILDER_HINT}"
    return text


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


def _namespace_image(image: str, org: str | None) -> str:
    """Prefix a bare image repository with the default org; keep namespaced refs as-is.

    `wordpress:latest` -> `<org>/wordpress:latest`; `websoft9dev/akeneo:v1` stays.
    """
    if not org:
        return image
    slash = image.rfind("/")
    colon = image.rfind(":")
    repository = image[:colon] if colon > slash else image
    if "/" in repository:
        return image
    return f"{org}/{image}"


def _dockerfile_plan(app_name: str, org: str | None = None) -> dict:
    """Plan a direct Dockerfile build (pull-only app). Per docs/image-tag-spec.md.

    Returns {version_arg, w9_version, w9_repo, images}; build must run with CWD = app dir.
    When `org` is set, a bare W9_REPO is published under that Docker Hub namespace.
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
    repo = _namespace_image(w9_repo, org)
    return {
        "version_arg": version_arg,
        "w9_version": w9_version,
        "w9_repo": repo,
        "images": [f"{repo}:{w9_version}"],
    }


def _stable_tags(repo: str, version: str) -> list[str]:
    if "-" in version:
        return [f"{repo}:{version}"]
    tags = [f"{repo}:latest"]
    part = ""
    for index, fragment in enumerate(version.split(".")):
        if index == 0:
            part = fragment
        else:
            part = f"{part}.{fragment}"
        tags.append(f"{repo}:{part}")
    return tags


def _resolve_dockerhub_org(env_file: str | None = None, org: str | None = None) -> str | None:
    if org:
        return org
    value = resolve_secret(DOCKERHUB_ORG_ENV, "dockerhub", env_file=env_file)
    return value or None


def build_plan(
    app_name: str,
    channel: str = "stable",
    git_sha: str | None = None,
    source_sha: str | None = None,
    org: str | None = None,
    env_file: str | None = None,
) -> dict:
    """Return the canonical image build/tag plan for one app.

    Channels:
    - stable: tags derived from W9_VERSION
    - dev: candidate tags dev-<git-sha> + dev-latest (build)
    - promote: stable tags; source is dev-<source_sha> when provided, otherwise
      the rolling dev-latest alias (re-tag, no build)

    This is the shared rules entrypoint for CI and controlled manual push.
    """
    source, compose = _load_compose(app_name)
    resolved_org = _resolve_dockerhub_org(env_file=env_file, org=org)
    plan = _dockerfile_plan(app_name, org=resolved_org)
    channel = (channel or "stable").strip().lower()
    version = plan["w9_version"]
    repo = plan["w9_repo"]
    if channel not in {"stable", "dev", "promote"}:
        raise ValueError(f"unsupported channel: {channel}")

    source_image = None
    if channel == "dev":
        resolved_sha = (git_sha or "").strip() or None
        if not resolved_sha:
            raise ValueError("git_sha is required for dev channel")
        short_sha = resolved_sha[:7]
        tags = [f"{repo}:dev-{short_sha}", f"{repo}:dev-latest"]
    else:
        tags = _stable_tags(repo, version)
        if channel == "promote":
            source_image = f"{repo}:{_promote_source_ref(source_sha)}"

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
        "org": resolved_org,
        "tags": tags,
        "source_image": source_image,
        "primary_image": source_image or tags[0],
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
    org: str | None = None,
    platform: str | None = None,
    binfmt: bool = True,
    registry: str | None = None,
    skip_sync: bool = False,
    compose_env_file: str | None = None,
    progress=None,
) -> dict:
    source, compose = _load_compose(app_name)
    build_services = _build_services(compose)
    platform_key = _resolve_platform(platform)
    multi_arch = platform_key == "both"
    platform_flag = PLATFORM_CHOICES[platform_key] if platform_key else None
    if build_services and platform_key not in (None, DEFAULT_PLATFORM):
        raise ValueError(
            f"app {app_name} uses compose build services; --platform {platform_key} "
            "is only supported for Dockerfile apps"
        )
    if multi_arch and not push:
        raise ValueError("--platform both builds a multi-arch manifest and requires --push")
    resolved_org = _resolve_dockerhub_org(env_file=env_file, org=org) if push else None

    if build_services:
        images = _tagged_images(source, compose, build_services)
        build_services_out = build_services
    else:
        plan = _dockerfile_plan(app_name, org=resolved_org)
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
        if platform_key and not build_services and binfmt:
            _ensure_binfmt_local(_required_binfmt_archs(platform_key, _local_arch()), progress=progress)
        pushed: list[str] = []
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
            build_result = _run_stream(build_command, progress=progress)
            if build_result.returncode != 0:
                raise RuntimeError(build_result.stdout.strip() or "docker build failed")
            if push:
                login_username, login_password = _resolve_dockerhub_credentials(env_file, username, password, token)
                _docker_login(registry, login_username, login_password, progress=progress)
                for image in images:
                    result = _run_stream(["docker", "push", image], progress=progress)
                    if result.returncode != 0:
                        raise RuntimeError(result.stdout.strip() or f"docker push failed for {image}")
                    pushed.append(image)
        elif multi_arch:
            login_username, login_password = _resolve_dockerhub_credentials(env_file, username, password, token)
            _docker_login(registry, login_username, login_password, progress=progress)
            build_command = [
                "docker",
                "buildx",
                "build",
                "--platform",
                platform_flag,
                "-f",
                str(source / "Dockerfile"),
                "--build-arg",
                f"{plan['version_arg']}={plan['w9_version']}",
                "-t",
                images[0],
                "--push",
                str(source),
            ]
            build_result = _run_stream(build_command, progress=progress)
            if build_result.returncode != 0:
                raise RuntimeError(_buildx_error(build_result.stdout))
            pushed = list(images)
        else:
            build_command = ["docker", "build"]
            if platform_flag:
                build_command += ["--platform", platform_flag]
            build_command += [
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
            "org": resolved_org,
            "platform": platform_key or "host",
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

    if platform_key and not build_services and binfmt:
        _ensure_binfmt_remote(
            host,
            user,
            secret_path,
            _required_binfmt_archs(platform_key, _remote_arch(host, user, secret_path)),
            progress=progress,
        )

    pushed = []
    if build_services:
        build_script = (
            f"docker compose --progress plain -f {app_target}/docker-compose.yml "
            f"--env-file {app_target}/.env build {' '.join(build_services)}"
        )
        build_result = remote.stream_ssh(host, user, secret_path, build_script, on_line=progress)
        if build_result.returncode != 0:
            raise RuntimeError(build_result.stdout.strip() or "remote docker build failed")
        if push:
            login_username, login_password = _resolve_dockerhub_credentials(env_file, username, password, token)
            _docker_login_remote(host, user, secret_path, registry, login_username, login_password, progress=progress)
            for image in images:
                result = remote.run_command(remote.ssh_base(host, user, secret_path) + [f"docker push {image}"])
                if result.returncode != 0:
                    raise RuntimeError(result.stdout.strip() or f"remote docker push failed for {image}")
                pushed.append(image)
    elif multi_arch:
        login_username, login_password = _resolve_dockerhub_credentials(env_file, username, password, token)
        _docker_login_remote(host, user, secret_path, registry, login_username, login_password, progress=progress)
        build_script = (
            f"cd {app_target} && docker buildx build --platform {platform_flag} -f Dockerfile "
            f"--build-arg {plan['version_arg']}={plan['w9_version']} -t {images[0]} --push ."
        )
        build_result = remote.stream_ssh(host, user, secret_path, build_script, on_line=progress)
        if build_result.returncode != 0:
            raise RuntimeError(_buildx_error(build_result.stdout))
        pushed = list(images)
    else:
        platform_arg = f" --platform {platform_flag}" if platform_flag else ""
        build_script = (
            f"cd {app_target} && docker build{platform_arg} -f Dockerfile "
            f"--build-arg {plan['version_arg']}={plan['w9_version']} -t {images[0]} ."
        )
        build_result = remote.stream_ssh(host, user, secret_path, build_script, on_line=progress)
        if build_result.returncode != 0:
            raise RuntimeError(build_result.stdout.strip() or "remote docker build failed")
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
        "org": resolved_org,
        "platform": platform_key or "host",
        "build_services": build_services_out,
        "images": images,
        "pushed": pushed,
        "push": push,
        "path": str(source.relative_to(repo_path())),
    }
