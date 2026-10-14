#!/bin/sh
# Start QwenPaw Hub (multi-user control plane) from the official image with a
# package-managed first administrator and the Local runtime backend.
set -e

export QWENPAW_WORKING_DIR="${QWENPAW_WORKING_DIR:-/app/working}"
export QWENPAW_HUB_DIR="${QWENPAW_HUB_DIR:-${QWENPAW_WORKING_DIR%/}/hub}"
HUB_CONFIG="${QWENPAW_WORKING_DIR%/}/hub.yaml"
export QWENPAW_HUB_CONFIG="${HUB_CONFIG}"
HUB_PORT="${QWENPAW_HUB_PORT:-8000}"

export QWENPAW_HUB_ADMIN_USER="${QWENPAW_HUB_ADMIN_USER:-admin}"
export QWENPAW_HUB_ADMIN_PASSWORD="${QWENPAW_HUB_ADMIN_PASSWORD:-}"

# The official image is the single-user Console image. It ships neither the
# Docker SDK that the Hub control plane imports at startup nor bubblewrap for
# the Local runtime backend, so install whatever is missing before booting Hub.
if ! python -c "import docker" >/dev/null 2>&1; then
  echo "Installing the QwenPaw Hub control-plane dependency (docker SDK)..."
  pip install --no-cache-dir "docker>=7.1.0,<8"
fi
if ! command -v bwrap >/dev/null 2>&1; then
  echo "Installing bubblewrap for the Local runtime backend..."
  apt-get update \
    && apt-get install -y --no-install-recommends bubblewrap \
    && rm -rf /var/lib/apt/lists/*
fi

mkdir -p "${QWENPAW_HUB_DIR}"

# Seed the first administrator once (the first registered account becomes the
# Hub administrator) and render the startup config. Both steps are done in
# Python so the same script works across QwenPaw Hub releases whose CLI and
# registration config schema differ.
python - <<'PY'
import json
import os
from pathlib import Path

from qwenpaw.hub.auth import HubAuthService
from qwenpaw.hub.control_app import get_hub_root
from qwenpaw.hub.credentials import TenantCredentialVault
from qwenpaw.hub import config as hub_config

root = Path(get_hub_root())
root.mkdir(parents=True, exist_ok=True)
database_path = root / "control.db"
vault = TenantCredentialVault(database_path, root / "secrets" / ".vault_key")
auth = HubAuthService(database_path, vault)

if not auth.has_enabled_admin():
    username = os.environ["QWENPAW_HUB_ADMIN_USER"]
    password = os.environ["QWENPAW_HUB_ADMIN_PASSWORD"]
    if not password:
        raise SystemExit("QWENPAW_HUB_ADMIN_PASSWORD is required on first startup")
    auth.register(username, password)
    print(f"Initialized the first QwenPaw Hub administrator: {username}")

registration: dict[str, object] = {}
registration_fields = hub_config.RegistrationConfig.model_fields
if "mode" in registration_fields:
    registration["mode"] = os.environ.get("QWENPAW_HUB_REGISTRATION_MODE", "open")
elif "enabled" in registration_fields:
    registration["enabled"] = (
        os.environ.get("QWENPAW_HUB_REGISTRATION_MODE", "open") != "closed"
    )
if "default_role" in registration_fields:
    registration["default_role"] = "user"

config = {
    "version": 1,
    "control_plane": {
        "public_base_url": os.environ["QWENPAW_HUB_PUBLIC_BASE_URL"],
        "registration": registration,
    },
    "runtime": {"provisioner": "local"},
    "capacity": {
        "max_running_runtimes": int(os.environ.get("QWENPAW_HUB_MAX_RUNTIMES", "20")),
    },
}
# Hub accepts YAML; JSON is a subset of YAML, so no extra dependency is needed.
Path(os.environ["QWENPAW_HUB_CONFIG"]).write_text(
    json.dumps(config, indent=2) + "\n",
    encoding="utf-8",
)
print("Rendered Hub startup config with public_base_url and Local runtime backend.")
PY

exec qwenpaw hub \
  --host 0.0.0.0 \
  --port "${HUB_PORT}" \
  --force-public \
  --config "${HUB_CONFIG}" \
  --log-level "${QWENPAW_HUB_LOG_LEVEL:-info}"
