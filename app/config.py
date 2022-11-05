import os


def get_video_folder():
    _default = "/Users/denys/experiments/junction-2022/app/static/video"
    return os.getenv("BASE_FOLDER", _default)


def get_library_folder():
    _default = "/Users/denys/experiments/junction-2022/app/static/library"
    return os.getenv("LIBRARY_FOLDER", _default)
