from flask import Flask, make_response, redirect, render_template, request

import random
import os
import uuid
import ujson

app = Flask(__name__, static_url_path='/static')

USER_ID_COOKIE = 'user_id'

with open('input/input.json', 'r') as f:
    data = ujson.load(f)


def init_annotations(user_annotation_file):
    EMPTY = {"sentences": []}

    with open(user_annotation_file, 'w') as f:
        ujson.dump(EMPTY, f, indent=2, ensure_ascii=False)

    return EMPTY


def get_annotations(user_id):
    user_annotation_file = f'annotations/{user_id}.json'

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
    user_id = request.cookies.get(USER_ID_COOKIE)
    
    if not user_id:
        user_id = str(uuid.uuid4())

    annotated = get_annotations(user_id)
    destination = len(annotated['sentences'])

    resp = make_response(redirect(f'/annotate/{destination}'))
    resp.set_cookie(USER_ID_COOKIE, user_id)

    return resp


@app.route("/annotate/<int:unclamped_sentence_id>")
def annotate(unclamped_sentence_id):
    user_id = request.cookies.get(USER_ID_COOKIE)

    if not user_id:
        return redirect('/')

    annotated = get_annotations(user_id)

    # Prevent user input from accessing out of bounds.
    sentence_id = min(len(data['sentences']) - 1, unclamped_sentence_id)

    try:
        user_target = annotated['sentences'][sentence_id]['target']
    except:
        user_target = None

    args = {
        'done': len(data['sentences']) <= unclamped_sentence_id,
        'user_id': user_id,
        'user_target': user_target,
        'name': 'Foobar',
        'sentence_id': sentence_id,
        'source': data['sentences'][sentence_id]['source'],
        'targets': enumerate(zip(random.sample(data['sentences'][sentence_id]['targets'], len(data['sentences'][sentence_id]['targets'])), 'asdjkl'))
    }

    return render_template('annotate.html', **args)


@app.route("/write_annotation/<int:sentence_id>/<sentence>")
def write_annotation(sentence_id, sentence):
    res = {'status': False}
    user_id = request.cookies.get(USER_ID_COOKIE)

    if user_id:
        annotated = get_annotations(user_id)

        if sentence_id <= len(annotated['sentences']) and sentence_id < len(data['sentences']):
            if sentence_id == len(annotated['sentences']):
                annotated['sentences'].append({'source': data['sentences'][sentence_id]['source'], 'target': sentence})
            else:
                print(sentence_id)
                annotated['sentences'][sentence_id] = {'source': data['sentences'][sentence_id]['source'], 'target': sentence}

            with open(f'annotations/{user_id}.json', 'w') as f:
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
