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
from app.conversor import (errors_rectangle, errors_square, generate_dxf,
                           get_errors_upload_topographical_file, get_layers,
                           get_layers_table, get_symbols,
                           upload_topographical_file, get_dxf_configuration)
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.upload_optional_files import (error_symbols, file_empty,
                                       get_config_file,
                                       get_errors_config_file_duplicate_elements,
                                       get_errors_config_file,
                                       get_errors_config_file_duplicate_color,
                                       upload_config_file, upload_symbols_file)

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
            filename_config = ''
            if f_config:
                filename_config = secure_filename(f_config.filename)
                f_config.save(os.path.join(
                    app.config["UPLOAD_FOLDER"], filename_config))
            upload_config_file("./tmp/" + filename_config)

            var_file_config_empty=file_empty(get_errors_config_file(), get_config_file())

            if get_errors_config_file():
                flash(
                    'Error: config file has the following errors. \
                        Check the file')
                return render_template('upload.html', title='Carga Archivos')
            elif get_errors_config_file_duplicate_elements() and not var_file_config_empty:
                flash(
                    'Error: config file has duplicate items on different lines. \
                        Check the file')
                return render_template('upload.html', title='Carga Archivos')

            elif get_errors_config_file_duplicate_color(get_config_file()) and not var_file_config_empty:
                flash(
                    'Error: config file has different colors on the same lines. \
                        Check the file')
                return render_template('upload.html', title='Carga Archivos')
            elif var_file_config_empty:
                flash(
                    'Error: config file is empty. \
                        Check the file')
                return render_template('upload.html', title='Carga Archivos')

            filename_symbols = ''
            if f_symbols:
                filename_symbols = secure_filename(f_symbols.filename)
                f_symbols.save(os.path.join(
                    app.config["UPLOAD_FOLDER"], filename_symbols))
            upload_symbols_file("./tmp/"+filename_symbols)

            f_topography.save(os.path.join(
                app.config["UPLOAD_FOLDER"], filename_topography))

            upload_topographical_file("./tmp/" + filename_topography)

            if get_errors_upload_topographical_file():
                flash(
                    'Error: topographic data file has the following errors. \
                         Check the file')
                return render_template('upload.html', title='Carga Archivos')
            if errors_square():
                flash(
                    'Error: The number of points with "TC" code is not \
                        multiple of 2. Check the file')
                return render_template('upload.html', title='Carga Archivos')
            if errors_rectangle():
                flash(
                    'Error: The number of points with "TR" code is not \
                        multiple of 3. Check the file')
                return render_template('upload.html', title='Carga Archivos')

            get_layers_table()

            return redirect(url_for("convert_file_dxf"))
        flash("Error: the topografic data file type must be: .txt o .csv.")

    return render_template('upload.html', title='Carga Archivos')


@app.route("/convert", methods=["GET", "POST"])
@login_required
def convert_file_dxf():

    form = request.form.to_dict()

    if request.method == "POST":

        cad_version=form['cadversion']
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
        print(layers)
        new_layers = get_dxf_configuration(layers)
        print(new_layers)
        # Provisional
        session['dxf_output'] = str(session['username']) + '_file.dxf'

        if get_errors_config_file_duplicate_color(new_layers):
            flash(
                'Error: config file has different colors on the same lines. \
                        Check the file')

            return render_template('convert.html', title='Conversion DXF', form=form,
                                   capas=get_layers_table(), symbols=get_symbols(),
                                   cad_versions=app.config["CAD_VERSIONS"],
                                   errores=get_errors_upload_topographical_file())

        else:
            generate_dxf("./tmp", session['dxf_output'],
                         layers,cad_version)
            return redirect(url_for("downloads"))

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
    return redirect(url_for('login'))
