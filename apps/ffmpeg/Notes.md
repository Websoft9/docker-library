# FFmpeg

CLI tool application; the container exits after each command, so the compose file uses `restart: "no"` by design (avoiding a restart loop).

## Usage

```
docker compose run --rm ffmpeg -version
docker compose run --rm ffmpeg -i /media/input.mp4 /media/output.mp4
```

The `/media` volume is shared for input and output files.
