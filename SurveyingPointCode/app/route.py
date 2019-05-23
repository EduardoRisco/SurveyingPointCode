# -*- coding: utf-8 -*-
# route.py
# Copyright (C) 2018,2019 J. Eduardo Risco
# version 1.0
#
# Module to manage server with Flask.

import os
import secrets
import shutil
import time
from zipfile import ZipFile, ZIP_DEFLATED

from flask import (flash, redirect, render_template, request,
                   send_from_directory, url_for, session)
from flask_login import (current_user, login_required,
                         login_user, logout_user)
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.conversor import (generate_dxf, get_errors_upload_topographical_file,
                           errors_rectangle, errors_square, upload_topographical_file,
                           get_layers_table, get_dxf_configuration)
from app.forms import LoginForm, RegistrationForm, UploadForm
from app.models import User
from app.route_helper import (add_session, check_files_errors, update_layers, check_DXF_ext,
                              user_logout, create_user_folder, save_upload_files)
from app.upload_optional_files import (upload_symbols_file, get_symbols, upload_config_file,
                                       file_empty, get_errors_config_file, get_config_file,
                                       get_errors_config_file_duplicate_elements,
                                       error_symbols)

app.secret_key = secrets.token_urlsafe(16)
db.create_all()

# Guarantees callback for login failures
@login_manager.unauthorized_handler
def unauthorized_callback():
    user_logout()
    flash('You must be logged in to access this page.')
    return redirect(url_for('login'))

# Check downtime (max. 5 min) before making any request
@app.before_request
def control_inactivity_period():
    if current_user.is_authenticated and 'username' in session \
            and ((time.time() - session['last_activity']) > 300):

        # Delete custom folders
        if os.path.exists(session['user_folder']):
            shutil.rmtree(session['user_folder'])
        # Close session and delete session variables
        logout_user()
        session.clear()
        # Redirect to "login" and show error
        flash('Error: You have exceeded your inactivity time! Please, sign in again!')
        return redirect(url_for('login'))
    else:
        # Renew last activity time
        session['last_activity'] = time.time()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and 'username' in session:
        return redirect(url_for('upload_file'))
    else:
        user_logout()

    post = False
    email = ''
    form = LoginForm()

    if request.method == 'POST':
        post = True

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Error: Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                add_session(user)
                user.last_access = session['current_access']
                db.session.commit()
                next_page = url_for('upload_file')
            return redirect(next_page)
        if form.email.data is not None:
            email = form.email.data
    return render_template('login.html', title='Sign In', form=form, post=post,
                           email=email)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and 'username' in session:
        return redirect(url_for('upload_file'))
    else:
        user_logout()

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
    return render_template('register.html', title='Register', form=form, post=post,
                           data=data)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if 'username' not in session:
        user_logout()

        # Reset variables to prevent page rollback
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

            # Create customized directory for each user
            create_user_folder()
            # Save topography files, configuration and symbols in the user folder
            save_upload_files(f_topo, f_config, f_symbols)
            # Analyze topography file
            upload_topographical_file(os.path.join(session['files_folder'],
                                                   session['topographical_file']))
            # Analyze the configuration file (if it exists)
            upload_config_file(os.path.join(session['files_folder'],
                                            session['config_file']))
            # Analyze and extract the symbols from the file (if it exists)
            upload_symbols_file(os.path.join(session['files_folder'],
                                             session['symbols_file']))

            return redirect(url_for("convert_file_dxf"))

    return render_template('upload.html', title='Upload Files', form=form, post=post)


@app.route("/convert", methods=["GET", "POST"])
@login_required
def convert_file_dxf():
    if 'username' not in session:
        user_logout()

    post = False
    form = request.form.to_dict()

    layers = []
    cad_version = ''

    # Load possible file errors
    errors, duplicate_color_errors, \
        cad_color_errors = check_files_errors(get_config_file(), post)

    if not errors:
        layers = get_layers_table()
    elif (get_errors_upload_topographical_file() or file_empty(
            os.path.join(session['files_folder'], session['topographical_file'])) or
          errors_square() or errors_rectangle()) \
            or (session['config_file'] and (
            get_errors_config_file() or file_empty(os.path.join(session['files_folder'],
                                                                session['config_file'])) or
            get_errors_config_file_duplicate_elements())) \
            or (session['symbols_file'] and error_symbols()):
        shutil.rmtree(session['files_folder'])

    if request.method == "POST":
        post = True
        cad_version = form['cadversion']
        del form['cadversion']
        session['dxf_filename'] = form['dxf_filename']
        del form['dxf_filename']

        # Check if the file extension is correct (dxf)
        check_DXF_ext()

        # Updating the layers
        layers.clear()
        layers = update_layers(form)

        # Load possible file errors
        errors, duplicate_color_errors,\
            cad_color_errors = check_files_errors(get_dxf_configuration(layers), post)

        if duplicate_color_errors or cad_color_errors:
            return render_template('convert.html', title='Conversion DXF', form=form,
                                   layers=layers,
                                   dxf_filename=session['dxf_filename'],
                                   cad_version=cad_version, symbols=get_symbols(),
                                   cad_versions=app.config["CAD_VERSIONS"],
                                   errors=errors,
                                   duplicate_color_errors=duplicate_color_errors,
                                   cad_color_errors=cad_color_errors)

        # Generate the DXF and add it to the list of user generated in the session
        converted = generate_dxf(session['files_folder'], session['dxf_filename'],
                                 layers, cad_version)
        if converted:
            session['converted_files'].append({'folder': session['files_folder'],
                                               'file': session['dxf_filename']})
            flash('File successfully converted!!!')
        else:
            flash('Error: File could not be generated!!!')

        return redirect(url_for("downloads"))

    return render_template('convert.html', title='Conversion DXF', form=form,
                           layers=layers,
                           dxf_filename=session['dxf_filename'],
                           cad_version=cad_version, symbols=get_symbols(),
                           cad_versions=app.config["CAD_VERSIONS"],
                           errors=errors,
                           duplicate_color_errors=duplicate_color_errors,
                           cad_color_errors=cad_color_errors)


@app.route("/download", methods=["GET", "POST"])
@login_required
def downloads():
    if 'username' not in session:
        user_logout()

    if request.method == "POST":
        return redirect(url_for("download_file"))

    return render_template('download.html')


@app.route('/download_files', defaults={'fileindex': -1})
@app.route('/download_files/<int:fileindex>')
@login_required
def download_file(fileindex):
    if 'username' not in session:
        user_logout()

    try:
        if fileindex >= 0:
            # Download the selected file
            file_folder = session['converted_files'][fileindex]['folder']
            file_name = session['converted_files'][fileindex]['file']
            return send_from_directory(file_folder, file_name, as_attachment=True)
        else:
            # Compress all in zip to return them
            i = 1
            with ZipFile(os.path.join(session['user_folder'], 'converted_files.zip'),
                         'w') as zip_directory:
                for file_to_zip in session['converted_files']:
                    zip_directory.write(os.path.join(file_to_zip['folder']
                                                     , file_to_zip['file']),
                                        os.path.join(str(i), file_to_zip['file']),
                                        compress_type=ZIP_DEFLATED)
                    i += 1

            zip_directory.close()
            return send_from_directory(session['user_folder'], 'converted_files.zip',
                                       as_attachment=True)
    except Exception as e:
        return str(e)


@app.route('/logout')
def logout():
    # Delete custom folders
    if 'user_folder' in session and os.path.exists(session['user_folder']):
        shutil.rmtree(session['user_folder'])
    logout_user()
    session.clear()

    return redirect(url_for('index'))

