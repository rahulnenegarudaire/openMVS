import os      
from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__)
app.secret_key = "secret key"
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads/images')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No valid files selected.')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        for file in files:
            if not allowed_file(file.filename):
                flash(message=f'{file.filename} is of an invalid type.')
            elif file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash(message=f'{file.filename} uploaded successfully.')
        return redirect('/')

def run_processing_command():
    os.system('echo "Upload complete. Running bash command..."')
    os.system('python3 ~/openmvs/MvgMvsPipeline.py uploads/images output')

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

@app.route("/compute/", methods=['POST'])
def compute():
    # flash("Computing. This will take a while.")
    # return redirect('/')
    global processing_thread
    processing_thread = threading.Thread(target=run_processing_command)
    processing_thread.start()
    while processing_thread.is_alive():
        flash(message=get_thread_status())
        
    return render_template('compute.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)