from app import app
from flask import render_template, request, flash, redirect, url_for, send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
from app.forms import LoginForm

from app.conversor import genera_dxf

from sqlalchemy import create_engine
engine = create_engine('postgresql://usr:pass@localhost:5432/sqlalchemy')


ALLOWED_EXTENSIONS = set(["txt", "csv"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for("upload_file"))
    return render_template('login.html', title='Sign In', form=form)


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
            # Se genera y se guarda el archivo dxf
            genera_dxf("./tmp/"+filename)
            os.remove("./tmp/"+filename)
            return redirect(url_for("downloads"))
        return "Seleccione un archivo tipo: .txt o .csv."
    return render_template('upload.html', title='Carga Archivos')


@app.route("/download", methods=["GET", "POST"])
def downloads():
    if request.method == "POST":
        return redirect(url_for("download_file", filename='salida.dxf'))
    return render_template('download.html')


@app.route('/download_files/<filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return str(e)
