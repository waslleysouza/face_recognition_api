import numpy as np
import cv2
import os
import io
import json
from datetime import datetime
from PIL import Image
import multiprocessing
import classifier
import align.align_dataset_mtcnn
import ffmpeg


# load settings
with open("deployment.json", 'r') as f:
    datastore = json.load(f)


UPLOAD_DIR  = datastore["UPLOAD_DIR"]
INPUT_DIR  = datastore["INPUT_DIR"]
OUTPUT_DIR = datastore["OUTPUT_DIR"]
MODEL_PATH = datastore["MODEL_PATH"]
CLASSIFIER_PATH = datastore["CLASSIFIER_PATH"]
STORAGE_BUCKET = datastore["STORAGE_BUCKET"]
SYNC_STORAGE_BUCKET = datastore["SYNC_STORAGE_BUCKET"]


def _get_content_type(file):
    return file.content_type.split("/")[1]


def _makedirs():
    for directory in [UPLOAD_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print("Folder", directory, "created!")


def classify(face_recognition, file):
    print("Method", "utils.classify")
    image = Image.open(io.BytesIO(file.read()))
    image = image.convert('RGB')

    # Resize uploaded images
    if image.size[1] >= datastore["IMAGE_WIDTH"]:
        wpercent = (datastore["IMAGE_WIDTH"] / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        image = image.resize((datastore["IMAGE_WIDTH"], hsize), Image.ANTIALIAS)

    image.save(os.path.join(UPLOAD_DIR, "classify_" + file.filename))
    image = np.array(image)
    faces = face_recognition.identify(image)

    if faces is not None:
        if faces[0]:
            print(faces[0].name)
            return json.dumps({'result': 'success', 'name': faces[0].name})
			
    return json.dumps({'result': 'success', 'message': 'error'})


def train():
    print("Method", "utils.train")
    align.align_dataset_mtcnn.main(align.align_dataset_mtcnn.parse_arguments([INPUT_DIR, OUTPUT_DIR]))
    classifier.main(classifier.parse_arguments(['TRAIN', OUTPUT_DIR, MODEL_PATH, CLASSIFIER_PATH]))


def add(file, name, rotate):
    print("Method", "utils.add")
    
    filename = "add_" + file.filename
    if _get_content_type(file) == 'png':
        file = Image.open(io.BytesIO(file.read()))
        file = file.convert('RGB')
        filename += ".jpg"
    file.save(os.path.join(UPLOAD_DIR, filename))
    file = os.path.join(UPLOAD_DIR, filename)

    try:
        probe = ffmpeg.probe(file)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            return json.dumps({'result': 'error', 'message': 'Invalid File!'})
    except:
        return json.dumps({'result': 'error', 'message': 'Invalid File!'})

    rotate = video_stream['tags']['rotate'] if 'tags' in video_stream and 'rotate' in video_stream['tags'] else rotate
    cap = cv2.VideoCapture(file)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_count = datastore["FRAMES_PER_VIDEO"] if frame_count > datastore["FRAMES_PER_VIDEO"] else frame_count
    frame_no = 0
    count = 1

    directory = os.path.join(INPUT_DIR, name)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Folder", directory, "created!")

    while frame_no <= frame_count:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ret, frame = cap.read()
        if ret:
            if rotate is not None:
                frame = cv2.rotate(frame, rotateCode=_get_rotate_code(int(rotate)))

            image_path = os.path.join(INPUT_DIR, name, "{}_{}_{}.jpg".format(name, datetime.now().strftime("%Y%m%d%H%M%S"), count))
            cv2.imwrite(image_path, frame)
            print("File", image_path, "created!")
            count += 1

            # TODO: Syncronize with cloud storage bucket
            # if SYNC_STORAGE_BUCKET:
                # opc_storage.create_or_replace_object(STORAGE_BUCKET, name + "/" + filename, frame)
                # print("Syncronized with cloud!")
        
        frame_no += 1
    
    return json.dumps({'result': 'success', 'message': 'File uploaded!'})


def _get_rotate_code(rotate):
    rotate_code = cv2.ROTATE_90_CLOCKWISE
    if rotate == 180:
        rotate_code = cv2.ROTATE_180
    elif rotate == 270:
        rotate_code = cv2.ROTATE_90_COUNTERCLOCKWISE
    return rotate_code


_makedirs()
#train()