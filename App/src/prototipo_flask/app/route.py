
import os
from app import app
from flask import render_template, request, flash, redirect, url_for, send_from_directory, send_file
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app.models import User
from app.forms import RegistrationForm, LoginForm
from app import db

from app.conversor import genera_dxf

ALLOWED_EXTENSIONS = set(["txt", "csv"])

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

db.create_all()

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload_file'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('upload_file')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route("/upload", methods=["GET", "POST"])
@login_required
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



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('upload_file'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

