#!/bin/bash

export IMAGEIO_FFMPEG_EXE="/Users/denys/Downloads/ffmpeg"
export BASE_FOLDER="/Users/denys/experiments/junction-2022/app/static/video"
export LIBRARY_FOLDER="/Users/denys/experiments/junction-2022/app/static/library"

python -m flask --debug run
