"""
This module serves as the API provider for face processing.
"""

import io
import os
import json
import face
import multiprocessing
import requests
import utils


# load settings
with open("deployment.json", 'r') as f:
    datastore = json.load(f)


VIDEO_DIR = os.path.join(datastore["UPLOAD_DIR"], "video")

processes = 3


def train():
    print("Method", "train")
    pool = multiprocessing.pool.ThreadPool(processes=processes)
    pool.apply_async(utils.train, callback=train_callback)
    pool.close()
    return json.dumps({'result': 'success', 'message': 'Model will be trained!'})
	

def train_callback(result):
    requests.get('http://localhost:5000/face/restart')


def restart():
    print("Method", "restart")
    global face_recognition
    face_recognition = face.Recognition()
    return json.dumps({'result': 'success', 'message': 'Model restarted!'})
	

def classify(file):
    print("Method", "classify")
    return utils.classify(face_recognition, file)


def add(file, personName, rotate):
    print("Method", "add")
    file.save(os.path.join(VIDEO_DIR, file.filename))
    pool = multiprocessing.pool.ThreadPool(processes=processes)
    pool.apply_async(utils.split_video, args=[file, personName, rotate])
    pool.close()
    return json.dumps({'result': 'success', 'message': 'Video uploaded!'})


face_recognition = face.Recognition()