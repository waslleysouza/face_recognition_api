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


# load settings
with open("deployment.json", 'r') as f:
    datastore = json.load(f)


INPUT_DIR  = datastore["INPUT_DIR"]
OUTPUT_DIR = datastore["OUTPUT_DIR"]
MODEL_PATH = datastore["MODEL_PATH"]
CLASSIFIER_PATH = datastore["CLASSIFIER_PATH"]
VIDEO_DIR = os.path.join(datastore["UPLOAD_DIR"], "video")
PHOTO_DIR = os.path.join(datastore["UPLOAD_DIR"], "photo")
STORAGE_BUCKET = datastore["STORAGE_BUCKET"]
SYNC_STORAGE_BUCKET = datastore["SYNC_STORAGE_BUCKET"]


def makedirs():
    for directory in [VIDEO_DIR, PHOTO_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print("Folder", directory, "created!")


def classify(face_recognition, file):
    image = Image.open(io.BytesIO(file.read()))

    # Resize uploaded images
    if image.size[1] < datastore["IMAGE_WIDTH"]:
        wpercent = (datastore["IMAGE_WIDTH"] / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        image = image.resize((datastore["IMAGE_WIDTH"], hsize), Image.ANTIALIAS)

    image.save(os.path.join(PHOTO_DIR, file.filename))
    image = np.array(image)
    faces = face_recognition.identify(image)

    if faces is not None:
        if faces[0]:
            print(faces[0].name)
            return json.dumps({'name': faces[0].name})
			
    return json.dumps({'name': 'null'})


def train():
    align.align_dataset_mtcnn.main(align.align_dataset_mtcnn.parse_arguments([INPUT_DIR, OUTPUT_DIR]))
    classifier.main(classifier.parse_arguments(['TRAIN', OUTPUT_DIR, MODEL_PATH, CLASSIFIER_PATH]))


def split_video(video, name, rotate):
    rotate = None if rotate is None or rotate == "0" else int(rotate)

    cap = cv2.VideoCapture(os.path.join(VIDEO_DIR, video.filename))
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
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
                frame = cv2.rotate(frame, rotateCode=_get_rotate_code(rotate))

            image_path = os.path.join(INPUT_DIR, name, "{}_{}_{}.jpg".format(name, datetime.now().strftime("%Y%m%d%H%M%S"), count))

            # Syncronize with cloud storage bucket
            if SYNC_STORAGE_BUCKET:
                # opc_storage.create_or_replace_object(STORAGE_BUCKET, name + "/" + filename, frame)
                print("Syncronized with cloud!")
                
            # Save locally
            cv2.imwrite(image_path, frame)
            print("File", image_path, "created!")
            frame_no += 1
            count += 1


def _get_rotate_code(rotate):
    rotate_code = cv2.ROTATE_90_CLOCKWISE
    if rotate == 180:
        rotate_code = cv2.ROTATE_180
    elif rotate == 270:
        rotate_code = cv2.ROTATE_90_COUNTERCLOCKWISE
    return rotate_code


makedirs()
#train()