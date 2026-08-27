from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from libs.repo import repo_path


DEFAULT_SECRET_PATH = ".secrets/ssh/default.pem"
DEFAULT_DEPLOY_ROOT = "/websoft9/library/apps"
DEFAULT_TARGET = "local"
DEFAULT_USER = "root"


def _profile_path() -> Path:
    # Resolve lazily so tests running in a temporary repo are not affected by
    # the developer's real .secrets/remote.env.
    return repo_path(".secrets", "remote.env")


def load_profile() -> dict[str, str]:
    profile = _profile_path()
    if not profile.exists():
        return {}
    data: dict[str, str] = {}
    for raw_line in profile.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def default_target() -> str:
    return (load_profile().get("TARGET") or DEFAULT_TARGET).lower()


def ssh_host(value: str | None = None) -> str | None:
    return value or load_profile().get("SSH_HOST")


def ssh_user(value: str | None = None) -> str:
    return value or load_profile().get("SSH_USER") or DEFAULT_USER


def ssh_secret_path(value: str | None = None) -> str:
    return value or load_profile().get("SSH_SECRET_PATH") or DEFAULT_SECRET_PATH


def deploy_root(value: str | None = None) -> str:
    return value or load_profile().get("DEPLOY_ROOT") or DEFAULT_DEPLOY_ROOT


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return repo_path(*path.parts)


def resolve_secret_path(path_value: str | None = None) -> Path:
    resolved = ssh_secret_path(path_value)
    path = Path(resolved)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] == ".secrets":
        return repo_path(*path.parts)
    return repo_path(".secrets", "ssh", *path.parts)


def secret_mode(secret_path: Path) -> str:
    sample = secret_path.read_text(encoding="utf-8", errors="ignore")[:256]
    if sample.lstrip().startswith("-----BEGIN "):
        return "key"
    return "password"


def ssh_connect_options() -> list[str]:
    # Dedicated ephemeral test servers: their public IP may be reimaged, so a
    # stale entry in the global ~/.ssh/known_hosts must never block automation.
    # Disable host-key checking and use /dev/null so no shared known_hosts is
    # read or written. Do not use for production or long-lived hosts.
    return [
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "ConnectTimeout=15",
    ]


def ssh_base(host: str, user: str, secret_path: Path) -> list[str]:
    base: list[str] = []
    if secret_mode(secret_path) == "key":
        base.extend(["ssh", "-i", str(secret_path)])
    else:
        if not shutil.which("sshpass"):
            raise FileNotFoundError("sshpass is required for password-based SSH; provide a key file or install sshpass")
        base.extend(["sshpass", "-f", str(secret_path), "ssh"])
    return base + ssh_connect_options() + [f"{user}@{host}"]


def scp_base(host: str, user: str, secret_path: Path) -> list[str]:
    base: list[str] = []
    if secret_mode(secret_path) == "key":
        base.extend(["scp", "-i", str(secret_path)])
    else:
        if not shutil.which("sshpass"):
            raise FileNotFoundError("sshpass is required for password-based SSH; provide a key file or install sshpass")
        base.extend(["sshpass", "-f", str(secret_path), "scp"])
    return base + ssh_connect_options()


def scrub_ssh_stderr(text: str) -> str:
    cleaned = []
    for line in text.splitlines():
        if line.startswith("Warning: Permanently added '") and "to the list of known hosts." in line:
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def scrub_completed_process(result: subprocess.CompletedProcess) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=result.args,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=scrub_ssh_stderr(result.stderr),
    )


def run_command(command: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return scrub_completed_process(result)


def run_ssh(host: str, user: str, secret_path: Path, script: str) -> subprocess.CompletedProcess:
    return run_command(ssh_base(host, user, secret_path) + [script])


def preflight_ssh(host: str, user: str, secret_path: Path) -> subprocess.CompletedProcess:
    return run_ssh(host, user, secret_path, "true")
