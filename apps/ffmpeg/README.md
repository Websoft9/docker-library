# FFmpeg on Docker  

This is an **[Docker Compose template](https://github.com/Websoft9/docker-library)** powered by [Websoft9](https://www.websoft9.com) based on Docker for FFmpeg:

 - community:  9.0, latest

## About

FFmpeg is a CPU-friendly media toolkit for offline batch jobs on a Linux server:

- Suits: remux/container conversion, audio processing, probing, thumbnails, subtitles, short/low-res transcoding, media library normalization
- Not for: real-time multi-stream transcoding or 4K re-encoding without a GPU

The container stays alive as a toolbox; run one-shot jobs with `exec` or `run`.

## System Requirements

The following are the minimal [recommended requirements](https://ffmpeg.org/documentation.html):

* **RAM**: 1 GB or more
* **CPU**: 1 cores or higher
* **Disk**: at least 1 GB of free space
* **bandwidth**: more fluent experience over 100M  

## Install

You can install this FFmpeg by [How to use it?](https://github.com/Websoft9/docker-library#how-to-use-it).   

If you want use FFmpeg with **Websoft9 Business Support** free, you can [subscribe FFmpeg](https://www.websoft9.com/apps) on Cloud platform

## Usage

```bash
docker compose up -d                                  # start the live toolbox
docker compose exec ffmpeg "ffmpeg -version"          # check version
docker compose exec ffmpeg "ffmpeg -i /media/in.mov /media/out.mp4"   # remux
docker compose exec ffmpeg "ffmpeg -i /media/in.mp4 -vf fps=1/10 /media/thumb%03d.jpg"  # thumbnails
docker compose run --rm ffmpeg "ffprobe -v error -show_format /media/in.mp4"  # one-shot probe
```

Put source files under the `media` volume or mount your own path.

## Documentation

[FFmpeg Administrator Guide](https://support.websoft9.com/docs/ffmpeg) powered by Websoft9
