from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from os.path import abspath

images_path = os.getenv('IMAGES_PATH') or abspath('../static/uploads')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = images_path
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
    app.run(debug=True, host='0.0.0.0')
