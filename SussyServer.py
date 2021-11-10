import re
from flask import Flask, request, render_template, flash, send_file
from werkzeug.utils import redirect
import os
from ImgToSus import ImgToSus

app = Flask(__name__)

HOME_PATH = app.root_path
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
UPLOAD_FOLDER = HOME_PATH + '/temporary/'
FILENAME_TEMPLATE = "$name_$key.$ext"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET'])
def main():
    return render_template("suspage.html", images=sorted(os.listdir(UPLOAD_FOLDER)[::-1]))

@app.route("/upload", methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            flash('No file part')

        file = request.files['file']
        if file.filename == '':
            flash('No file selected')

        if file and allowed_file(file.filename):
            filename = get_correct_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imageConverted = ImgToSus(scale=7)
            imageConverted.load_img(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            result_path = imageConverted.convert_img()
            remove_file(filename)

            return redirect(f"/temporary/{result_path}")
        return flash("Wrong file format! Need jpg or jpeg")
    except Exception as e:
        return str(e)

@app.route('/temporary/<filename>', methods=['GET', 'POST'])
def download(filename):
    try:
        temp = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        result = send_file(temp + filename, attachment_filename=filename)
        remove_file(temp + filename)
        return result
    except Exception as e:
        return str(e)

def get_correct_filename(filename):
    name_ext = filename.rsplit('.', 1)
    return FILENAME_TEMPLATE.replace("$ext", name_ext[1].lower()).replace("$name", name_ext[0]).replace("$key", name_ext[0])

def remove_file(filename):
    print(filename)
    if "/" in filename or "." in filename:
        os.system(f"rm {filename}")
    else:
        os.system(f"rm {UPLOAD_FOLDER + filename}")

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER   
    app.run(debug=False, host='0.0.0.0')