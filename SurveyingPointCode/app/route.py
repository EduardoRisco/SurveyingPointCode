# -*- coding: utf-8 -*-
#
# Module to manage server with Flask
#
# J. Eduardo Risco 01-04-2019
#

import os
import secrets
import shutil
import time

from flask import (flash, redirect, render_template, request, send_file,
                   send_from_directory, session, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.conversor import (errors_rectangle, errors_square, generate_dxf,
                           get_code_layers, get_dxf_configuration,
                           get_errors_upload_topographical_file,
                           get_layers_table, get_symbols,
                           upload_topographical_file)
from app.forms import LoginForm, RegistrationForm, UploadForm
from app.models import User
from app.route_helper import (add_session, create_user_folder,
                              save_upload_files, user_logout)
from app.upload_optional_files import (
    error_symbols, file_empty, get_config_file, get_errors_cad_color_palette,
    get_errors_config_file, get_errors_config_file_duplicate_color,
    get_errors_config_file_duplicate_elements, upload_config_file,
    upload_symbols_file)

app.secret_key = secrets.token_urlsafe(16)
db.create_all()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('upload_file'))

    post = False
    email = ''
    form = LoginForm()
    if request.method == 'POST':
        post = True
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Error: Invalid email or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                add_session(user)
                user.last_access = session['current_access']
                db.session.commit()
                next_page = url_for('upload_file')
            return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, email=email, post=post)


@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('upload_file'))
    post = False
    data = {
        'username': '',
        'email': ''
    }
    form = RegistrationForm()

    if request.method == 'POST':
        post = True
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('You are now a registered user!')
            return redirect(url_for('login'))
        if form.username.data is not None:
            data['username'] = form.username.data
        if form.email.data is not None:
            data['email'] = form.email.data
    return render_template('register.html', title='Register', form=form, post=post, data=data)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if 'username' not in session:
        user_logout()  

    # Reiniciar variables para prevenir retroceso de pagina
    session['topographical_file'] = ''
    session['config_file'] = ''
    session['symbols_file'] = ''
    session['files_folder'] = ''
    session['dxf_filename'] = '' 
    f_config = ""
    f_symbols = ""
    f_topo = ""

    post = False
    form = UploadForm()

    if request.method == 'POST':
        post = True          

        if form.validate_on_submit():
            if "config_file" in request.files:
                f_config = request.files["config_file"]

            if "symbols_file" in request.files:
                f_symbols = request.files["symbols_file"]      

            f_topo = request.files["topographical_file"]
            session['topographical_file'] = secure_filename(f_topo.filename)
            
            # Crear directorio particularizado para cada usuario
            create_user_folder()
            # Guardar archivos de campo, configuracion y simbolos en la carpeta del usuario
            save_upload_files(f_topo, f_config, f_symbols) 
            # Analizar archivo de campo
            upload_topographical_file(os.path.join(session['files_folder'], session['topographical_file']))
            # Analizar el archivo de configuración (si existe)
            upload_config_file(os.path.join(session['files_folder'], session['config_file']))
            # Analizar y extraer los simbolos del archivo (si existe)
            upload_symbols_file(os.path.join(session['files_folder'], session['symbols_file']))

            return redirect(url_for("convert_file_dxf"))

    return render_template('upload.html', title='Upload Files', form=form, post=post)


@app.route("/convert", methods=["GET", "POST"])
@login_required
def convert_file_dxf():

    form = request.form.to_dict()

    if request.method == "POST":

        cad_version = form['cadversion']
        del form['cadversion']

        # Actualizar las capas
        layers = []
        layer = {}
        i = 0

        for key in form.keys():
            field, index = key.split('-')
            if int(index) != i:
                layers.append(layer)
                layer = {}
                i += 1
            layer.update({field: form[key]})
        layers.append(layer)

        new_layers = get_dxf_configuration(layers)

        # Provisional
        session['dxf_output'] = str(session['username']) + '_file.dxf'

        if get_errors_config_file_duplicate_color(new_layers, get_code_layers()):
            flash(
                'Error: config file has different colors on the same lines. \
                        Check the file')

            return render_template('convert.html', title='Conversion DXF', form=form,
                                   capas=get_layers_table(), symbols=get_symbols(),
                                   cad_versions=app.config["CAD_VERSIONS"],
                                   errores=get_errors_upload_topographical_file())
        else:
            if generate_dxf("./tmp", session['dxf_output'], layers, cad_version):

                flash('Successfully converted file')
                return redirect(url_for("downloads"))
            else:
                flash('Error: converted file')
                return render_template('upload.html', title='Carga Archivos')

    return render_template('convert.html', title='Conversion DXF', form=form,
                           capas=get_layers_table(), symbols=get_symbols(),
                           cad_versions=app.config["CAD_VERSIONS"],
                           errores=get_errors_upload_topographical_file())


@app.route("/download", methods=["GET", "POST"])
@login_required
def downloads():
    if request.method == "POST":
        return redirect(url_for("download_file"))
    return render_template('download.html')


@app.route('/download_files')
@login_required
def download_file():
    try:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            session['dxf_output'],
            as_attachment=True)
    except Exception as e:
        return str(e)


@app.route('/logout')
@login_required
def logout():

    logout_user()
    session.clear()
    return redirect(url_for('index'))
