import random
import os
import glob
import datetime
from multiprocessing import Pool
import hashlib

from flask import Flask, render_template, request
from flask import send_file

from overlay_pipeline import TextConfig, TargetResolution, overlay_image
import config

import variance_utils as variance

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
    fonts = ["static/fonts/arial.ttf", "static/fonts/Gingerbread House.ttf", "static/fonts/Montez-Regular.ttf"]
    font= random.choice(fonts)
    text = input.metadata["caption"]
    font_size = 50
    if len(text) > 15:
        font_size = 36
    elif len(text) > 25:
        font_size = 24

    text_config1 = TextConfig(text,
                              font=font,
                              size=font_size,
                              position_x=input.text_pos_x,
                              position_y=input.text_pos_y,
                              color=input.color)

    absolute_path = config.get_video_folder()
    subfolder = f'result-{input.metadata["job_id"]}/'
    os.makedirs(os.path.join(absolute_path, subfolder), exist_ok=True)
    file_name = subfolder + f'out-{input.id}.mp4'
    overlay_image("static/video/" + input.metadata["video_path"],
                  "static/video/" + input.metadata["image_path"],
                  position_x=input.image_pos_x,
                  position_y=input.image_pos_y,
                  out_path=os.path.join(absolute_path, file_name),
                  text_configs=[text_config1],
                  target_resolution=TargetResolution(target_width=480, target_height=850))
    return file_name


def render_videos(metadata):
    input_1 = RenderInput(metadata=metadata,
                          color=(255, 255, 255, 255),
                          text_pos_x=30,
                          text_pos_y=600,
                          id=1,
                          image_pos_x=50,
                          image_pos_y=50)
    input_2 = RenderInput(metadata=metadata, color=(0, 0, 0, 0), text_pos_x=40, text_pos_y=600, id=2,
                          image_pos_x=70,
                          image_pos_y=600
                          )
    input_3 = RenderInput(metadata=metadata, color=(255, 0, 0, 0), text_pos_x=10, text_pos_y=700, id=3,
                          image_pos_x=400,
                          image_pos_y=0
                          )
    input_4 = RenderInput(metadata=metadata,
                          color=(333, 22, 11, 255),
                          text_pos_x=10,
                          text_pos_y=300,
                          id=4,
                          image_pos_x=400,
                          image_pos_y=700)
    input_5 = RenderInput(metadata=metadata, color=(123,90, 0, 0), text_pos_x=30, text_pos_y=300, id=5,
                          image_pos_x=200,
                          image_pos_y=100
                          )
    input_6 = RenderInput(metadata=metadata, color=(300, 0, 200, 0), text_pos_x=10, text_pos_y=400, id=6,
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

@app.route('/generated_content')
def generated_content():
    for dirname, dirnames, filenames in os.walk('static/video'):
        dir_names = sorted(dirnames)
        return render_template('generated_content.html', folders=dir_names)

@app.route('/videos/<job_id>')
def videos(job_id):
    filenames = os.listdir(os.path.join("static/video", job_id))
    video_list = [f'{job_id}/{filename}' for filename in filenames]
    return render_template('videos.html', videos=video_list, project_directory=job_id)


def _get_library_category(base_name):
    parts = base_name.split("/")
    if len(parts) > 0:
        return parts[-2]
    return "other"


def _sample_library_files(category_files, sample_size=30):
    if len(category_files) <= sample_size:
        return category_files
    return random.choices(category_files, k=sample_size)


def _get_image_id(image_file):
    return hashlib.md5(image_file.encode()).hexdigest()


def _get_image_base_map():
    library_folder = config.get_library_folder()
    if not library_folder.endswith("/"):
        library_folder = library_folder + "/"
    library_files = list(glob.iglob(os.path.join(library_folder, '**/*.png'), recursive=True))
    return {_get_image_id(f):f for f in library_files}


def _get_image_file_from_image_id(image_id):
    image_base_map = _get_image_base_map()
    return image_base_map.get(image_id, "")


@app.route('/library_content/<image_id>')
def show_image(image_id):
    image_file = _get_image_file_from_image_id(image_id)
    return send_file(image_file, mimetype='image/png')


@app.route('/library_similar')
def library_similar():
    image_id = request.args.get('selection')
    image_file = _get_image_file_from_image_id(image_id)
    sel_image = variance.get_image_from_file(image_file)
    top_rank = variance.variation_find_similar(sel_image)
    context = {
        'ref_image': image_id,
        'image_list': [_get_image_id(t[0]) for t in top_rank]
    }
    return render_template('library_reference.html', context=context)


@app.route('/library_variance')
def library_variance():
    image_id = request.args.get('selection')
    image_file = _get_image_file_from_image_id(image_id)
    sel_image = variance.get_image_from_file(image_file)
    image_variations = variance.get_image_variations(sel_image)
    file_variations = variance.write_variance_images(image_variations)
    image_id_list = [_get_image_id(f) for f in file_variations]
    context = {
        'ref_image': image_id,
        'image_list': image_id_list
    }
    return render_template('library_reference.html', context=context)


@app.route('/library_create')
def library_create():
    q = request.args.get('q')
    if q:
        image_list = variance.get_image_from_text(q)
        file_list = variance.write_ai_images(image_list)
        image_id_list = [_get_image_id(f) for f in file_list]
    else:
        q = ""
        image_id_list = []

    context = {
        'q': q,
        'image_list': image_id_list
    }
    return render_template('library_create.html', context=context)


@app.route('/library')
def library():
    image_base_map = _get_image_base_map()
    category_map = {}
    for image_id, base_path in image_base_map.items():
        category = _get_library_category(base_path)
        if category not in category_map:
            category_map[category] = []
        category_map[category].append(image_id)
    context = {
        'library_emoji': _sample_library_files(category_map.get('openmoji', [])),
        'library_people': _sample_library_files(category_map.get('people', [])),
        'library_ai': _sample_library_files(category_map.get('ai', [])),
        'library_variance': _sample_library_files(category_map.get('variance', []))
    }
    return render_template('library.html', context=context)
