import re
from flask import Flask, request, render_template, flash, send_from_directory, redirect
import os
from ImgToSus import ImgToSus
import uuid

app = Flask(__name__)

HOME_PATH = app.root_path
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
UPLOAD_FOLDER = 'temporary'
FILENAME_TEMPLATE = "$key.$ext"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET'])
def main(): 
    converted = request.args.get('converted')
    uploaded = request.args.get('uploaded')
    return render_template("suspage.html", folder=app.config['UPLOAD_FOLDER'], converted=converted, uploaded=uploaded)

@app.route("/upload", methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')

    if file and allowed_file(file.filename):
        converted_filename = None
        key, uploaded_filename = get_correct_filename(file.filename)
        path = os.path.join(app.root_path, UPLOAD_FOLDER, uploaded_filename)
        print(f"Saving image {path}")
        file.save(path)
        try:
            imageConverted = ImgToSus(scale=5, root=app.root_path)
            imageConverted.load_img(path)
            converted_filename = imageConverted.convert_img(key=key)
            return redirect(f"/?converted={converted_filename}&uploaded={uploaded_filename}")
        except Exception as e:
            remove_file(path)
            if converted_filename != None:
                remove_file(os.path.join(app.root_path, UPLOAD_FOLDER, converted_filename))
            flash(str(e))
            return redirect("/")
    
    flash("Wrong file format! Need jpg or jpeg")
    return redirect("/")

@app.route('/temporary/<filename>', methods=['GET', 'POST'])
def download(filename):
    folder = os.path.join(app.root_path, UPLOAD_FOLDER)
    return send_from_directory(folder, filename)

def get_correct_filename(filename: str) -> str:
    filename = filename.replace("/", "\/")
    name_n_ext = filename.rsplit('.', 1)
    key = get_key(name_n_ext[0])
    return key, FILENAME_TEMPLATE.replace("$ext", name_n_ext[1].lower()).replace("$key", key)

def get_key(filename)-> str:
    return uuid.uuid4().hex + filename

def remove_file(filename):
    os.remove(filename)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER   
    app.run(debug=False, host='0.0.0.0')