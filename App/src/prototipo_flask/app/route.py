from app import app
from flask import render_template, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os


ALLOWED_EXTENSIONS = set(["txt", "csv"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if not "file" in request.files:
            return "No ha seleccionado ningún archivo."
        f = request.files["file"]
        if f.filename == "":
            return "No ha seleccionado ningún archivo."
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            
            return redirect(url_for("get_file", filename=filename))
        return "Seleccione un archivo tipo: .txt o .csv."

    return render_template('upload.html', title='Carga Archivos')


@app.route("/uploads/<filename>")
def get_file(filename):
    return render_template('uploads.html', title='Uploads', filename=filename)
