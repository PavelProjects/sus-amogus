from flask import Flask, request, render_template, flash, url_for
from werkzeug.utils import redirect
import os
from ImgToSus import ImgToSus

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
UPLOAD_FOLDER = './static/'

app = Flask(__name__)
imageConverted = ImgToSus()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET'])
def main():
    return render_template("suspage.html", images=sorted(os.listdir(UPLOAD_FOLDER)[::-1]))

@app.route("/upload", methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')

    # if file and allowed_file(file.filename):
    #   file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.jpg'))
    imageConverted.load_img(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.jpg'), resize=False)
    imageConverted.convert_img()
    imageConverted.save_converted_image()

    return redirect("/")

    

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER   
    app.run(debug=False, host='0.0.0.0')