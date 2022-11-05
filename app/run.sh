#!/bin/bash

export IMAGEIO_FFMPEG_EXE="/Users/denys/Downloads/ffmpeg"
export BASE_FOLDER="/Users/denys/experiments/junction-2022/app/static/video"

python -m flask --debug run
