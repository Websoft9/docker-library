#!/usr/bin/env bash
set -euo pipefail

logdir="${TENSORBOARD_LOGDIR:-/tf/notebooks/logs}"
mkdir -p "${logdir}"

if [[ "${TENSORBOARD_DEMO:-true}" == "true" && -f /opt/w9/seed_demo.py && ! -f "${logdir}/demo/.seeded" ]]; then
  echo "Seeding TensorBoard demo data into ${logdir}/demo"
  if TENSORBOARD_DEMO_LOGDIR="${logdir}/demo" python /opt/w9/seed_demo.py; then
    touch "${logdir}/demo/.seeded"
  else
    echo "TensorBoard demo seeding failed; continuing without demo data"
  fi
fi

if [[ -f /opt/w9/tensorboard_demo.py && ! -f /tf/notebooks/tensorboard_demo.py ]]; then
  cp /opt/w9/tensorboard_demo.py /tf/notebooks/tensorboard_demo.py
fi

if [[ "${TENSORBOARD_AUTOSTART:-true}" == "true" ]]; then
  echo "Starting TensorBoard on 0.0.0.0:6006 with logdir ${logdir}"
  tensorboard --logdir "${logdir}" --bind_all --port 6006 &
fi

set +u
source /etc/bash.bashrc
set -u

cmd=(
  jupyter notebook
  --notebook-dir=/tf/notebooks
  --ip 0.0.0.0
  --no-browser
  --allow-root
  --ServerApp.allow_password_change=False
)

if [[ -n "${JUPYTER_TOKEN:-}" ]]; then
  cmd+=(--ServerApp.token="${JUPYTER_TOKEN}")
fi

exec "${cmd[@]}"
