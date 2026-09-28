# CHANGELOG

## 2026-09-21

- Updated Tensorflow community package from `2.19.0-jupyter` to `2.20.0-jupyter`.
- Normalized `.env` and `docker-compose.yml` to current repository policy for variable formatting and port comments.
- Added app-specific functional test coverage metadata for the Jupyter entry path.

## 2026-09-23

- Filled the missing `variables.json` fields: `upstream.docs`, `access`, `credentials`, `env`, and `help`.
- Rewrote `README.md` to the current repository structure and removed the stale `Notes.md`.
- Replace the random startup token with a fixed token wired from `W9_LOGIN_PASSWORD` so the Access tab can show a stable login secret.
- Start TensorBoard automatically at container launch and move the default Jupyter working directory to `/tf/notebooks` so notebooks and logs land on the persisted volume.
- Seed a small `demo` TensorBoard run on first start (disable with `TENSORBOARD_DEMO=false`) and ship `tensorboard_demo.py` so the dashboard shows charts immediately.
- Fix the `PS1: unbound variable` startup crash caused by sourcing `/etc/bash.bashrc` under `set -u`.
- Declare the `admin` access surface (`/lab` on 8888) alongside `web` and `metrics`.
