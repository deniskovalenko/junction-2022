#heavily inspired by https://github.com/anajetli/python_video_editing

import cv2
import numpy as np
import os
##todo make it proper :)
os.environ["IMAGEIO_FFMPEG_EXE"] = "/Users/denys/Downloads/ffmpeg"
####
import moviepy.editor as mpe
import matplotlib.pyplot as plt
import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import PILasOPENCV as ImageFont
from typing import List


class TextConfig:
    def __init__(self, text: str, font: str, size: int, position_x: int, position_y: int) -> None:
        self.text = text
        self.font = font
        self.size = size
        self.position_x = position_x
        self.position_y = position_y


def add_transparent_image(background, foreground, x_offset=None, y_offset=None):
    bg_h, bg_w, bg_channels = background.shape
    fg_h, fg_w, fg_channels = foreground.shape

    assert bg_channels == 3, f'background image should have exactly 3 channels (RGB). found:{bg_channels}'
    assert fg_channels == 4, f'foreground image should have exactly 4 channels (RGBA). found:{fg_channels}'

    # center by default
    if x_offset is None: x_offset = (bg_w - fg_w) // 2
    if y_offset is None: y_offset = (bg_h - fg_h) // 2

    w = min(fg_w, bg_w, fg_w + x_offset, bg_w - x_offset)
    h = min(fg_h, bg_h, fg_h + y_offset, bg_h - y_offset)

    if w < 1 or h < 1: return

    # clip foreground and background images to the overlapping regions
    bg_x = max(0, x_offset)
    bg_y = max(0, y_offset)
    fg_x = max(0, x_offset * -1)
    fg_y = max(0, y_offset * -1)
    foreground = foreground[fg_y:fg_y + h, fg_x:fg_x + w]
    background_subsection = background[bg_y:bg_y + h, bg_x:bg_x + w]

    # separate alpha and color channels from the foreground image
    foreground_colors = foreground[:, :, :3]
    alpha_channel = foreground[:, :, 3] / 255  # 0-255 => 0.0-1.0

    # construct an alpha_mask that matches the image shape
    alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

    # combine the background with the overlay image weighted by alpha
    composite = background_subsection * (1 - alpha_mask) + foreground_colors * alpha_mask

    # overwrite the section of the background image that has been updated
    background[bg_y:bg_y + h, bg_x:bg_x + w] = composite


''' ***** ***** ***** ***** ***** ***** *****
Generate Video with Image Background -- Start
***** ***** ***** ***** ***** ***** ***** '''


def overlay_image(video_path, image_path, out_path, text_configs: List[TextConfig]):
    video = cv2.VideoCapture(video_path)
    image = cv2.imread(image_path)

    def nothing():
        pass

    # videowriter
    framespersecond = float(video.get(cv2.CAP_PROP_FPS))
    # todo can be smaller
    res = (1920, 1080)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, framespersecond, res)


    overlay = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    # image = cv2.resize(image, (1920, 1080))

    done = False;

    while not done:
        ret, video_frame = video.read()

        if not ret:
            done = True
            continue

        video_frame = cv2.resize(video_frame, (1920, 1080))


        add_transparent_image(video_frame, overlay, 0, -20)

        im = Image.fromarray(cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(im)

        for text_config in text_configs:
            font = ImageFont.truetype(text_config.font, text_config.size)  # ("AvenirLTStd-Black.ttf", scale)
            wtf_is_this = (244, 172, 58)
            draw.text((text_config.position_x, text_config.position_y), text_config.text, font=font, fill=wtf_is_this)
        video_frame = im.getim()

        out.write(video_frame)

    video.release()
    out.release()


''' ***** ***** ***** ***** ***** ***** *****
Generate Video with Image Background -- End
***** ***** ***** ***** ***** ***** ***** '''

if __name__ == "__main__":
    text_config = TextConfig("Hello, Junction!",
                             "arial.ttf",
                             48,
                             370,
                             952)

    overlay_image("video/2.mov", "video/Subject.png", "video/out.mp4", [text_config])
