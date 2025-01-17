import os
import subprocess
from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename
import threading
from random import random
from math import floor

app = Flask(__name__)
app.secret_key = "secret key"
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads/images')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'mp4'])
TOKEN = str(floor(random()*1000))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():

    UNIQUE_FOLDER = os.path.join(path, TOKEN)
    os.mkdir(f"{UNIQUE_FOLDER}")
    os.mkdir(os.path.join(f"{UNIQUE_FOLDER}", "uploads"))
    os.mkdir(os.path.join(f"{UNIQUE_FOLDER}", "output"))
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No valid files selected.')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        for file in files:
            if not allowed_file(file.filename):
                flash(message=f'{file.filename} is of an invalid type.')
            elif file:
                file.save(os.path.join(UNIQUE_FOLDER,
                          "uploads", file.filename))
                flash(
                    message=f'{file.filename} uploaded successfully with token {TOKEN}. Please remember this.')
        return redirect('/')


def run_photogrammetry_command():
    os.system('echo "Upload complete. Running bash command to start photogrammetry..."')
    os.system(
        f'python3 ~/openMVS/MvgMvsPipeline.py {TOKEN}/uploads {TOKEN}/output')


def run_detection_command():
    os.system('echo "Upload complete. Running bash command to start object detection..."')
    os.system(
        f'python3 ~/objectDetection/yolov8_tracking/track.py --source {TOKEN}/uploads --output {TOKEN}/output')


@app.route('/status')
def get_thread_status():
    if processing_thread is None:
        status = "No processing is being done currently."
    elif processing_thread.is_alive():
        status = "Processing is ongoing."
    else:
        status = "Processing finished."
    return status
    # return render_template('status.html', status=status)


@app.route("/computePhotogrammetry/", methods=['POST'])
def computePhotogrammetry():
    # flash("Computing. This will take a while.")
    # return redirect('/')
    global processing_thread
    processing_thread = threading.Thread(target=run_photogrammetry_command)
    processing_thread.start()
    # while processing_thread.is_alive():
    #     flash(message=get_thread_status())

    return render_template('compute.html')


@app.route("/computeObjectDetection/", methods=['POST'])
def computeObjectDetection():
    # flash("Computing. This will take a while.")
    # return redirect('/')
    global processing_thread
    processing_thread = threading.Thread(target=run_detection_command)
    processing_thread.start()
    # while processing_thread.is_alive():
    #     flash(message=get_thread_status())

    return render_template('compute.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
