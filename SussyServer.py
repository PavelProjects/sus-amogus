from flask import Flask, request, render_template, flash, send_from_directory, redirect
import os
from ImgToSus import ImgToSus

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

HOME_PATH = app.root_path
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
UPLOAD_FOLDER = 'temporary'
FILENAME_TEMPLATE = "$name_$key.$ext"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET'])
def main():
    converted = request.args.get('converted')
    uploaded = request.args.get('uploaded')
    result = render_template("suspage.html", converted=converted, uploaded=uploaded)
    remove_file(os.path.join(app.root_path, UPLOAD_FOLDER, uploaded))
    remove_file(os.path.join(app.root_path, UPLOAD_FOLDER, converted))
    return result


@app.route("/upload", methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')

    if file and allowed_file(file.filename):
        converted_filename = None
        uploaded_filename = get_correct_filename(file.filename)
        path = os.path.join(app.root_path, UPLOAD_FOLDER, uploaded_filename)
        print(f"Saving image {path}")
        file.save(path)
        try:
            imageConverted = ImgToSus(scale=5, root=app.root_path)
            imageConverted.load_img(path)
            converted_filename = imageConverted.convert_img()
            return redirect(f"/?converted={converted_filename}&uploaded={uploaded_filename}")
        except:
            remove_file(path)
            if converted_filename != None:
                remove_file(os.path.join(app.root_path, UPLOAD_FOLDER, converted_filename))
    flash("Wrong file format! Need jpg or jpeg")
    return redirect("/")

@app.route("/download/<path:filename>")
def download(filename):
    folder = os.path.join(app.root_path, UPLOAD_FOLDER)
    print(folder + filename)
    return send_from_directory(folder, filename)

def get_correct_filename(filename: str):
    filename = filename.replace("/", "\/")
    name_ext = filename.rsplit('.', 1)
    return FILENAME_TEMPLATE.replace("$ext", name_ext[1].lower()).replace("$name", name_ext[0]).replace("$key", name_ext[0])

def remove_file(filename):
    os.system(f"rm {filename}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')