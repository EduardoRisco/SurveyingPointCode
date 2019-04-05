# -*- coding: utf-8 -*-
#
# Module to manage server with Flask
#
# J. Eduardo Risco 01-04-2019
#

import os
import secrets
import time

from flask import (flash, redirect, render_template, request, send_file,
                   send_from_directory, session, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.conversor import (cad_versions, configuration_table, genera_dxf,
                           get_errors_rectangle, get_errors_square,
                           get_errors_upload, get_layers, upload_txt, get_symbols, configuration_table)
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.upload_optional_files import (extract_symbols, get_errors_config_user,
                                       get_errors_config_user_duplicate_elements,
                                       upload_file_config)

app.secret_key = secrets.token_urlsafe(16)
db.create_all()


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    email = ''
    if current_user.is_authenticated:
        return redirect(url_for('upload_file'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Error: Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('upload_file')
            session['username'] = user.username
            session['last_access'] = user.last_access
            session['current_access'] = time.ctime(time.time())
            user.last_access = session['current_access']
            db.session.commit()
            flash('User successfully logged in')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, email=email)


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


return_web_config = [{'code': 'RE', 'layer': 'Red_Electrica',
                      'color': 'rgb(120, 120, 120)', 'symbol': 'No symbol found'},
                     {'code': 'A', 'layer': 'Acera',
                      'color': 'rgb(0, 0, 0)', 'symbol': 'No symbol found'},
                     {'code': 'SAN', 'layer': 'Saneamiento',
                      'color': 'rgb(0, 0, 255)', 'symbol': 'No symbol found'},
                     {'code': 'TEL', 'layer': 'Telecomunicaciones',
                      'color': 'rgb(0, 255, 0)', 'symbol': 'No symbol found'},
                     {'code': 'FA', 'layer': 'Farola',
                      'color': 'rgb(255, 0, 0)', 'symbol': 'Farola'},
                     {'code': 'V', 'layer': 'Vertice',
                      'color': 'rgb(0, 0, 0)', 'symbol': 'Vertice'},
                     {'code': 'E', 'layer': 'Edificio',
                      'color': 'rgb(38, 140, 89)', 'symbol': 'No symbol found'},
                     {'code': 'ARB', 'layer': 'Arbol',
                      'color': 'rgb(0, 255, 255)', 'symbol': 'Arbol'},
                     {'code': 'M', 'layer': 'Muro', 'color': 'rgb(255, 255, 0)', 'symbol': 'No symbol found'}]


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():

    if request.method == "POST":
        if "topographical_file" not in request.files:
            flash("Error: topographic data file not selected.")
            return render_template('upload.html', title='Carga Archivos')
        f_topography = request.files["topographical_file"]
        if "config_file" not in request.files:
            f_config = ""
        else:
            f_config = request.files["config_file"]
        if "symbols_file" not in request.files:
            f_symbols = ""
        else:
            f_symbols = request.files["symbols_file"]

        if f_topography.filename == "":
            flash("Error: topographic data file not selected.")
        if f_topography:
            filename_topography = secure_filename(f_topography.filename)

            if f_config:
                filename_config = secure_filename(f_config.filename)
                f_config.save(os.path.join(
                    app.config["UPLOAD_FOLDER"], filename_config))
                upload_file_config("./tmp/" + filename_config)
                if get_errors_config_user():
                    flash(
                        'Error: config file has the following errors. \
                         Check the file')
                    # return render_template('upload.html', title='Carga Archivos')
                elif get_errors_config_user_duplicate_elements():
                    flash(
                        'Error: config file has duplicate items on different lines. \
                         Check the file')
                    # return render_template('upload.html', title='Carga Archivos')

            if f_symbols:
                filename_symbols = secure_filename(f_symbols.filename)
                f_symbols.save(os.path.join(
                    app.config["UPLOAD_FOLDER"], filename_symbols))
                extract_symbols("./tmp/"+filename_symbols)

            f_topography.save(os.path.join(
                app.config["UPLOAD_FOLDER"], filename_topography))

            upload_txt("./tmp/" + filename_topography)
           

            # os.remove("./tmp/"+filename)
            if get_errors_upload():
                flash(
                    'Error: topographic data file has the following errors. \
                         Check the file')
                return render_template('upload.html', title='Carga Archivos')
            if get_errors_square():
                flash(
                    'Error: The number of points with "TC" code is not \
                        multiple of 2. Check the file')
                return render_template('upload.html', title='Carga Archivos')
            if get_errors_rectangle():
                flash(
                    'Error: The number of points with "TR" code is not \
                        multiple of 3. Check the file')
                return render_template('upload.html', title='Carga Archivos')

            configuration_table()
            return redirect(url_for("convert_file_dxf"))
        flash("Error: the topografic data file type must be: .txt o .csv.")

    return render_template('upload.html', title='Carga Archivos')


@app.route("/convert", methods=["GET", "POST"])
@login_required
def convert_file_dxf():

    form = request.form.to_dict()

    if request.method == "POST":

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

        # Provisional
        session['dxf_output'] = str(session['username']) + '_file.dxf'
        genera_dxf("./tmp", session['dxf_output'],
                   layers)
        return redirect(url_for("downloads"))

    return render_template('convert.html', title='Conversion DXF', form=form,
                           capas=configuration_table(), symbols=get_symbols(),  errores=get_errors_upload())


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
    return redirect(url_for('login'))
