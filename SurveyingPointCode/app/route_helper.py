# -*- coding: utf-8 -*-
# route_helper.py
# Copyright (C) 2018,2019 J. Eduardo Risco
# version 1.0
#
# Module containing auxilary functions associated with route.py


import os
import time
from datetime import date

from flask import session
from flask_login import logout_user
from werkzeug.utils import secure_filename

from app import app
from app.conversor import (get_code_layers, get_errors_upload_topographical_file,
                           errors_rectangle, errors_square)
from app.upload_optional_files import (file_empty, get_errors_config_file,
                                       get_errors_config_file_duplicate_elements,
                                       get_errors_config_file_duplicate_color,
                                       get_errors_cad_color_palette, error_symbols)

TOPOGRAPHIC_PARSER_ERROR = 'Topographic data file has the following errors.'
EMPTY_TOPOGRAPHIC_FILE = 'Topographic data file is empty.'
SQUARE_ERROR = 'The number of points with "TC" code in the topographic data file' \
               ' is not multiple of 2.'
RECTANGLE_ERROR = 'The number of points with "TR" code in the topographic data' \
                  ' file is not multiple of 3.'
CONFIG_PARSER_ERROR = 'User configuration file file has the following errors.'
EMPTY_CONFIG_FILE = 'User configuration file is empty.'
DUPLICATE_ELEMENTS = 'User configuration file has duplicate items on different lines.'
DUPLICATE_COLORS = 'User configuration has different colors on the same lines.'
CAD_COLORS_ERROR = 'Some color of the user configuration is not a CAD color.'
SYMBOLS_ERROR = 'CAD symbols file does not contain blocks.'


def add_session(user):
    """
    This function adds variables to the user session.
    """
    session['username'] = user.username
    session['current_access'] = date.today()
    session['last_access'] = user.last_access
    session['entry_time'] = str(time.time())
    session['user_folder'] = os.path.join(app.config["UPLOAD_FOLDER"],
                                          session['username'] + session['entry_time'])
    session['topographical_file'] = ''
    session['config_file'] = ''
    session['symbols_file'] = ''
    session['files_folder'] = ''
    session['dxf_filename'] = ''
    session['converted_files'] = []
    session['last_activity'] = time.time()
    session['id'] = ''


def user_logout():
    """
    This function closes the session and deletes the session variables.
    """
    logout_user()
    session.pop('username', None)
    session.pop('current_access', None)
    session.pop('last_access', None)
    session.pop('entry_time', None)
    session.pop('user_folder', None)
    session.pop('topographical_file', None)
    session.pop('config_file', None)
    session.pop('symbols_file', None)
    session.pop('files_folder', None)
    session.pop('dxf_filename', None)
    session.pop('converted_files', None)
    session.pop('last_activity', None)
    session.pop('id', None)


def create_user_folder():
    """
    This function creates, from each uploaded topographical data file name,
    a customized directory for each user.
    """
    new_file_folder = str(time.time())
    # Separate file name from extension
    f_topo_name, ext = os.path.splitext(session['topographical_file'])
    # Create User Session Folder
    if not os.path.exists(session['user_folder']):
        os.mkdir(session['user_folder'])

        # Create folder to host user files
    session['files_folder'] = os.path.join(session['user_folder'],
                                           f_topo_name + new_file_folder)
    if not os.path.exists(session['files_folder']):
        os.mkdir(session['files_folder'])


def save_upload_files(f_topo, f_config, f_symbols):
    """
    This function saves topographical data file, user configuration
    file and CAD symbols file in the user folder.
    """
    f_topo.save(os.path.join(
        session['files_folder'], secure_filename(f_topo.filename)))
    if f_config:
        session['config_file'] = secure_filename(f_config.filename)
        f_config.save(os.path.join(
            session['files_folder'], session['config_file']))
    if f_symbols:
        session['symbols_file'] = secure_filename(f_symbols.filename)
        f_symbols.save(os.path.join(
            session['files_folder'], session['symbols_file']))


def check_files_errors(layers, post):
    """
    This function checks possible files errors.
    """
    errors = []
    duplicate_color_errors = {}
    cad_color_errors = {}
    topographic_errors = []
    config_errors = []

    if get_errors_upload_topographical_file():
        topographic_errors.append(
            {'message': TOPOGRAPHIC_PARSER_ERROR,
             'errors': get_errors_upload_topographical_file()})
    else:
        if file_empty(os.path.join(session['files_folder'],
                                   session['topographical_file'])):
            topographic_errors.append({'message': EMPTY_TOPOGRAPHIC_FILE})
        else:
            if errors_square():
                topographic_errors.append({'message': SQUARE_ERROR})
            if errors_rectangle():
                topographic_errors.append({'message': RECTANGLE_ERROR})

    if session['config_file'] or post:
        if get_errors_config_file():
            config_errors.append({'message': CONFIG_PARSER_ERROR,
                                  'errors': get_errors_config_file()})
        else:
            if file_empty(os.path.join(session['files_folder'],
                                       session['config_file'])):
                config_errors.append({'message': EMPTY_CONFIG_FILE})
            else:
                if get_errors_config_file_duplicate_elements():
                    config_errors.append(
                        {'message': DUPLICATE_ELEMENTS,
                         'errors': get_errors_config_file_duplicate_elements()})
                if get_errors_config_file_duplicate_color(layers, get_code_layers()):
                    duplicate_color_errors = {'message': DUPLICATE_COLORS,
                                              'errors': get_errors_config_file_duplicate_color(layers,
                                                                                               get_code_layers())}
                if get_errors_cad_color_palette(layers, get_code_layers()):
                    cad_color_errors = {'message': CAD_COLORS_ERROR,
                                        'errors': get_errors_cad_color_palette(layers, get_code_layers())}

    if topographic_errors:
        errors.append(topographic_errors)
    if config_errors:
        errors.append(config_errors)
    if session['symbols_file'] and error_symbols():
        errors.append([{'message': SYMBOLS_ERROR}])

    return errors, duplicate_color_errors, cad_color_errors


def check_DXF_ext():
    """
    This function checks if the extension of the file name assigned
    by the user to the DXF file to be obtained is correct (dxf).
    """
    if session['dxf_filename'] == '':
        f_topo_name, ext = os.path.splitext(session['topographical_file'])
        session['dxf_filename'] = f_topo_name + ".dxf"
    else:
        session['dxf_filename'] = secure_filename(session['dxf_filename'])
        extension = session['dxf_filename'].split('.')
        if len(extension) > 1:
            if extension[-1].lower() != 'dxf':
                session['dxf_filename'] += '.dxf'
        else:
            session['dxf_filename'] += '.dxf'


def update_layers(form):
    """
    This function updates the layers according to the values entered in the form
    """
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

    return layers
