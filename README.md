# Face Recognition API

![Architecture](architecture.png)


## Basic Instalation - Steps

UBUNTU: If you are using Ubuntu, run: $ sudo apt-get install -y libsm6 libxext6 libxrender-dev ffmpeg

WINDOWS: If you are using Windows, download FFmpeg (https://www.ffmpeg.org/download.html) and add the bin folder to your system path.

1) Create a new Python or Anaconda environment: $ conda create -n facerec python=3.6 -y
2) Activate your environment: $ activate facerec
3) Install the packages of the requirement.txt file: 
    - If you have CPU: $ pip install -r requirement-cpu.txt
    - If you have GPU: $ pip install -r requirement-gpu.txt
4) Start the application: $ python server.py
5) Open your browser and access the Console: http://<HOST_IP_OR_LOCALHOST>:5000/ui


## Oracle Cloud Infrastructure Object Storage - Steps

It is possible to download or upload all your images to Oracle Cloud Infrastructure Object Storage.

1) Open the deployment.json file and change the following parameter:
    - "OCI_STORAGE_SYNC": true

2) Update the config/config.prod file with your Oracle Cloud Account information.


## Mobile Application

Use ![Face Recognition Mobile App](https://github.com/waslleysouza/face_recognition_mobile_app) as your mobile app.


## Usage

1) /face/add: This operation adds a new human face to the Face Recognition API database. You can upload videos or images that contain only one person.
2) /face/classify: This opertaion to execute a face recognition. You can upload images that contains only one person.
3) /face/train: This operation trains the model to recognize the new faces added by the "/face/add" operation.
4) /face/restart: This operation reloads the Face Recognition API model if you experience any problems.


## Inspiration

I use the ![Facenet](https://github.com/davidsandberg/facenet) implementation in this code.


## License

This project is ![MIT License](LICENSE.md)