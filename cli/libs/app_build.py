from __future__ import annotations

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


def _load_compose(app_name: str) -> tuple[Path, dict]:
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)
    compose_path = target / "docker-compose.yml"
    if not compose_path.exists():
        raise FileNotFoundError(compose_path)
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
    return target, compose


def _build_services(compose: dict) -> list[str]:
    services = compose.get("services") or {}
    return [name for name, service in services.items() if isinstance(service, dict) and service.get("build")]


def _tagged_images(compose: dict, services: list[str]) -> list[str]:
    all_services = compose.get("services") or {}
    images: list[str] = []
    for name in services:
        service = all_services.get(name) or {}
        image = service.get("image")
        if isinstance(image, str) and image not in images:
            images.append(image)
    return images


def _run_stream(command: list[str], progress=None) -> subprocess.CompletedProcess:
    return remote.stream_command(command, on_line=progress)


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


def build_app(
    app_name: str,
    push: bool = False,
    env_file: str | None = None,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    registry: str | None = None,
    progress=None,
) -> dict:
    target, compose = _load_compose(app_name)
    build_services = _build_services(compose)
    if not build_services:
        raise ValueError(f"app {app_name} has no build services")

    images = _tagged_images(compose, build_services)
    if push and not images:
        raise ValueError(f"app {app_name} build services have no image tags to push")

    build_result = _run_stream(
        [
            "docker",
            "compose",
            "--progress",
            "plain",
            "-f",
            str(target / "docker-compose.yml"),
            "--env-file",
            str(target / ".env"),
            "build",
            *build_services,
        ],
        progress=progress,
    )
    if build_result.returncode != 0:
        raise RuntimeError(build_result.stdout.strip() or "docker compose build failed")

    pushed: list[str] = []
    if push:
        login_password = token or password or resolve_secret(DOCKERHUB_TOKEN_ENV, "dockerhub", env_file=env_file) or resolve_secret(DOCKERHUB_PASSWORD_ENV, "dockerhub", env_file=env_file)
        login_username = username or resolve_secret(DOCKERHUB_USER_ENV, "dockerhub", env_file=env_file)
        if not login_username or not login_password:
            raise FileNotFoundError(
                "missing Docker Hub credentials; set DOCKERHUB_USERNAME and DOCKERHUB_PASSWORD or DOCKERHUB_TOKEN in env or .secrets/dockerhub.env"
            )
        _docker_login(registry, login_username, login_password, progress=progress)
        for image in images:
            result = _run_stream(["docker", "push", image], progress=progress)
            if result.returncode != 0:
                raise RuntimeError(result.stdout.strip() or f"docker push failed for {image}")
            pushed.append(image)

    return {
        "app": app_name,
        "build_services": build_services,
        "images": images,
        "pushed": pushed,
        "push": push,
        "path": str(target.relative_to(repo_path())),
    }
