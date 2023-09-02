import os
from os.path import abspath
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

static_path = os.getenv('STATIC_PATH') or abspath('../static')
upload_path = f'{static_path}/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_path
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')
        filenames = []

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filenames.append(filename)

        if filenames:
            return f"Uploaded images: {', '.join(filenames)}"
        else:
            return "No valid files uploaded."

    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return f"Uploaded image: {filename}"

if __name__ == '__main__':
    Path(upload_path).mkdir(parents=True, exist_ok=True)
    app.run(debug=True, host='0.0.0.0')
