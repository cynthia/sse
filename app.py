from flask import Flask, make_response, redirect, render_template, request

import random
import os
import uuid
import ujson


app = Flask(__name__, static_url_path='/static')
USER_ID_COOKIE = 'user_id'
DEFAULT_CONFIG = {'top_k': 1000}
data = {}
config = {}
projects = []

projects_scratch = os.listdir('projects')

for project in projects_scratch:
    project_path = os.path.join('projects', project)

    if os.path.isdir(project_path):
        project_json = f'projects/{project}/input/input.json'

        if os.path.exists(project_json):
            print(f'Loading project file {project_json}')
            projects.append(project)

            with open(project_json, 'r') as f:
                data[project] = ujson.load(f)

            project_config = f'projects/{project}/config.json'

            if os.path.exists(project_config):
                with open(project_config, 'r') as f:
                    config[project] = ujson.load(f)
            else:
                config[project] = DEFAULT_CONFIG

del projects_scratch


def init_annotations(user_annotation_file):
    EMPTY = {"sentences": []}

    with open(user_annotation_file, 'w') as f:
        ujson.dump(EMPTY, f, indent=2, ensure_ascii=False)

    return EMPTY


def get_annotations(user_id, project):
    user_annotation_file = f'projects/{project}/annotations/{user_id}.json'

    if os.path.exists(user_annotation_file):
        with open(user_annotation_file, 'r') as f:
            try:
                annotated = ujson.load(f)
            except:
                # FIXME: This doesn't account for invalid permissions tripping the wire.
                annotated = init_annotations(user_annotation_file)
    else:
        annotated = init_annotations(user_annotation_file)

    return annotated


@app.route("/")
def index():
    global projects

    user_id = request.cookies.get(USER_ID_COOKIE)
    
    if not user_id:
        user_id = str(uuid.uuid4())

    resp = make_response(render_template('projects.html', projects=projects, user_id=user_id))
    resp.set_cookie(USER_ID_COOKIE, user_id)

    return resp


@app.route("/go/<project>")
def go(project):
    global data
    project_json = f'projects/{project}/input/input.json'

    if not os.path.exists(project_json):
        return redirect('/')

    user_id = request.cookies.get(USER_ID_COOKIE)

    if not user_id:
        user_id = str(uuid.uuid4())

    annotated = get_annotations(user_id, project)
    destination = len(annotated['sentences'])

    resp = make_response(redirect(f'/annotate/{project}/{destination}'))
    resp.set_cookie(USER_ID_COOKIE, user_id)

    return resp


@app.route("/annotate/<project>/<int:unclamped_sentence_id>")
def annotate(project, unclamped_sentence_id):
    global data

    user_id = request.cookies.get(USER_ID_COOKIE)

    if not user_id:
        return redirect('/')

    annotated = get_annotations(user_id, project)

    # Prevent user input from accessing out of bounds.
    sentence_id = min(len(data[project]['sentences']) - 1, unclamped_sentence_id)

    try:
        user_target = annotated['sentences'][sentence_id]['target']
    except:
        user_target = None

    args = {
        'done': len(data[project]['sentences']) <= unclamped_sentence_id,
        'user_id': user_id,
        'user_target': user_target,
        'name': 'Foobar',
        'sentence_id': sentence_id,
        'source': data[project]['sentences'][sentence_id]['source'],
        'targets': enumerate(zip(data[project]['sentences'][sentence_id]['targets'], range(len(data[project]['sentences'][sentence_id]['targets']))))
    }

    return render_template('annotate.html', **args)


@app.route("/write_annotation/<project>/<int:sentence_id>/<sentence>")
def write_annotation(project, sentence_id, sentence):
    global data

    res = {'status': False}
    user_id = request.cookies.get(USER_ID_COOKIE)

    if user_id:
        annotated = get_annotations(user_id, project)

        if sentence_id <= len(annotated['sentences']) and sentence_id < len(data[project]['sentences']):
            if sentence_id == len(annotated['sentences']):
                annotated['sentences'].append({'source': data[project]['sentences'][sentence_id]['source'], 'target': sentence})
            else:
                print(sentence_id)
                annotated['sentences'][sentence_id] = {'source': data[project]['sentences'][sentence_id]['source'], 'target': sentence}

            with open(f'projects/{project}/annotations/{user_id}.json', 'w') as f:
                ujson.dump(annotated, f, indent=2, ensure_ascii=False)

            res['status'] = True

    return res


@app.route("/next_annotation/<user_id>")
def next_annotation(user_id):
    user_annotation_file = f'annotations/{user_id}.json'
    destination = 0

    if os.path.exists(user_annotation_file):
        with open(user_annotation_file, 'r') as f:
            try:
                annotated = ujson.load(f)
                destination = len(annotated['sentences'])
            except:
                # FIXME: This doesn't account for invalid permissions tripping the wire.
                init_annotations(user_annotation_file)
    else:
        init_annotations(user_annotation_file)

    return redirect(f'/annotate/{destination}')
