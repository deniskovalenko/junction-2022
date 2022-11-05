import random
import sys
import os
from flask import Flask, render_template, request
import datetime
from overlay_pipeline import TextConfig, TargetResolution, overlay_image
from multiprocessing import Pool

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


class RenderInput:
    def __init__(self, metadata, color, text_pos_x, text_pos_y, id,image_pos_x, image_pos_y):
        self.metadata = metadata
        self.color = color
        self.text_pos_x = text_pos_x
        self.text_pos_y = text_pos_y
        self.id=id
        self.image_pos_x=image_pos_x
        self.image_pos_y=image_pos_y


def render_video(input: RenderInput):
    text_config1 = TextConfig(input.metadata["caption"],
                              "static/fonts/arial.ttf",
                              size=50,
                              position_x=input.text_pos_x,
                              position_y=input.text_pos_y,
                              color=input.color)

    absolute_path = "/Users/denys/experiments/junction-2022/app/static/video/"
    relative_path = f'out-{input.metadata["job_id"]}-{input.id}.mp4'
    overlay_image("static/video/" + input.metadata["video_path"],
                  "static/video/" + input.metadata["image_path"],
                  position_x=input.image_pos_x,
                  position_y=input.image_pos_y,
                  out_path=os.path.join(absolute_path, relative_path),
                  text_configs=[text_config1],
                  target_resolution=TargetResolution(target_width=480, target_height=850))
    return relative_path


def render_videos(metadata):
    input_1 = RenderInput(metadata=metadata,
                          color=(255, 255, 255, 255),
                          text_pos_x=70,
                          text_pos_y=600,
                          id=1,
                          image_pos_x=50,
                          image_pos_y=50)
    input_2 = RenderInput(metadata=metadata, color=(0, 0, 0, 0), text_pos_x=100, text_pos_y=600, id=2,
                          image_pos_x=70,
                          image_pos_y=600
                          )
    input_3 = RenderInput(metadata=metadata, color=(255, 0, 0, 0), text_pos_x=10, text_pos_y=700, id=3,
                          image_pos_x=400,
                          image_pos_y=0
                          )
    input_4 = RenderInput(metadata=metadata,
                          color=(333, 22, 11, 255),
                          text_pos_x=70,
                          text_pos_y=300,
                          id=4,
                          image_pos_x=400,
                          image_pos_y=700)
    input_5 = RenderInput(metadata=metadata, color=(123,90, 0, 0), text_pos_x=70, text_pos_y=300, id=5,
                          image_pos_x=200,
                          image_pos_y=100
                          )
    input_6 = RenderInput(metadata=metadata, color=(300, 0, 200, 0), text_pos_x=200, text_pos_y=400, id=6,
                          image_pos_x=400,
                          image_pos_y=300
                          )
    with Pool(6) as p:
        results = p.map(render_video, [input_1, input_2, input_3, input_4, input_5, input_6])

    return results


@app.route('/render_video', methods=['GET', 'POST'])
def handle_data():
    video_path = request.form['video_path']
    image_path = request.form['image_path']
    caption = request.form['caption']
    job_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    metadata = {
        "job_id": job_id,
        "video_path": video_path,
        "image_path": image_path,
        "caption": caption
    }

    video_names = render_videos(metadata)
    return render_template('videos.html', videos=video_names), 422


@app.route('/videos/<job_id>')
def videos(job_id):
    video_list = [f'{job_id}-{x}.mp4' for x in range(1,7)]
    return render_template('videos.html', videos=video_list)
