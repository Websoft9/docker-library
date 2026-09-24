# Tensorflow on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Tensorflow**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open `http://<host>:${W9_HTTP_PORT_SET}/lab` from the **Access** tab.
2. Paste the token from the **Access** tab (`W9_LOGIN_PASSWORD`) into the JupyterLab login page. `W9_LOGIN_USER` is a display label only.
3. Open TensorBoard at `http://<host>:${W9_GUI_PORT_SET}`. It starts automatically and reads logs from `/tf/notebooks/logs`.
4. On first start the package seeds a small `demo` run, so TensorBoard shows an `accuracy`/`loss` chart immediately even before you run any training.
5. For real data, open the seeded `tensorboard_demo.py` in `/tf/notebooks`, run it, then refresh TensorBoard. To also embed it in a notebook, use `%load_ext tensorboard` and `%tensorboard --logdir /tf/notebooks/logs --bind_all`.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update `W9_LOGIN_PASSWORD` (or `W9_POWER_PASSWORD`) in `.env` and save.
3. Recreate the app so JupyterLab restarts with the new token.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Tensorflow Docker image](https://hub.docker.com/r/tensorflow/tensorflow) and makes some improvements below.

<!-- W9_NOTE_START -->
- The package uses the upstream Jupyter-enabled Tensorflow image and persists notebooks under `/tf/notebooks`.
- JupyterLab runs from `/tf/notebooks`, so new notebooks and TensorBoard logs stay on the persisted volume by default.
- The login token is fixed through `W9_LOGIN_PASSWORD`, which makes the Access tab usable without reading container logs.
- TensorBoard is exposed on `${W9_GUI_PORT_SET}` and starts automatically with logdir `/tf/notebooks/logs` unless you override `TENSORBOARD_LOGDIR`.
- On first start the package seeds a `demo` run (scalars, histogram, text) so TensorBoard is not empty. Set `TENSORBOARD_DEMO=false` in `.env` and recreate to skip it.
- A sample training script is copied to `/tf/notebooks/tensorboard_demo.py` so you can generate real charts with the TensorBoard Keras callback.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.20.0-jupyter, latest-jupyter.


### Ports

| Purpose | Port |
| --- | --- |
| JupyterLab | 8888 |
| TensorBoard | 6006 |


### Data Directory


Data is persisted in the `tensorflow` volume, mounted at `/tf/notebooks`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/entrypoint.sh` → `/usr/local/bin/w9-tensorflow-entrypoint.sh`
- `./src/seed_demo.py` → `/opt/w9/seed_demo.py`
- `./src/tensorboard_demo.py` → `/opt/w9/tensorboard_demo.py`



## References

- [Tensorflow Administrator Guide](https://support.websoft9.com/docs/tensorflow) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/tensorflow/tensorflow)

- [Official docs](https://www.tensorflow.org/install/docker)

- [GitHub docs](https://github.com/tensorflow/tensorflow)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**Notebook page asks for a token?**
- Use the token shown in the **Access** tab (`W9_LOGIN_PASSWORD`). If you changed it in `.env`, recreate the app so JupyterLab picks up the new value.

**TensorBoard is blank?**
- `No dashboards are active for the current data set` means TensorBoard is up but no event files exist under `/tf/notebooks/logs`. Seed data is written to `/tf/notebooks/logs/demo` unless `TENSORBOARD_DEMO=false`; run `tensorboard_demo.py` in `/tf/notebooks`, or update `TENSORBOARD_LOGDIR` and recreate the app.

**How do I embed TensorBoard inside a notebook?**
- Load the extension with `%load_ext tensorboard`, then run `%tensorboard --logdir /tf/notebooks/logs --bind_all`. `--bind_all` is required inside Docker so the embedded view can reach the server.

**Container exits unexpectedly?**
- Check `docker compose logs ${W9_ID}` for the Jupyter startup output.
<!-- W9_TROUBLESHOOT_END -->
