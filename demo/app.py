import os      
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret key"
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
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


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
