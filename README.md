# Face Recognition

![Architecture](architecture.png)


### FACE RECOGNITION SERVER

If you are using Ubuntu, run: sudo apt-get install -y libsm6 libxext6 libxrender-dev

If you are using Windows, download FFmpeg (https://www.ffmpeg.org/download.html) and add the bin folder to your system path.

1) Update the deployment.json file with your credentials and folders information.
2) Create a new Python or Anaconda environment: conda create -n facerec python=3.6 -y
3) Activate your environment: activate facerec
4) Install the packages of the requirement.txt file using PIP: pip install -r requirement.txt
5) Start the application: python server.py
6) Open your browser and access: http://<HOST_IP_OR_LOCALHOST>:5000/ui


### OPERATIONS

1) /face/add: Add new faces to the model
2) /face/classify: Execute the face recognition
3) /face/restart: Reload the model
4) /face/train: Train the model with new faces


### Inspiration

I use the ![Facenet](https://github.com/davidsandberg/facenet) implementation in this code.