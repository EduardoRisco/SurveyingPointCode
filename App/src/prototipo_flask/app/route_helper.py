# -*- coding: utf-8 -*-
#
# Module containing auxilary functions associated with route.py
#
# J. Eduardo Risco 16-04-2019
#

import os
import time
from datetime import datetime

from flask import session
from flask_login import logout_user
from werkzeug.utils import secure_filename

from app import app


def add_session(user):
    """
    This function adds variables to the user session.
    """
    session['username'] = user.username
    session['current_access'] = datetime.now()
    session['last_access'] = user.last_access
    session['entry_time'] = str(time.time())
    session['last_activity'] = time.time()
    session['user_folder'] = os.path.join(
        app.config["UPLOAD_FOLDER"], session['username'] + session['entry_time'])
    session['topographical_file'] = ''
    session['config_file'] = ''
    session['symbols_file'] = ''
    session['files_folder'] = ''
    session['new_file_folder'] = ''


def user_logout():
    """
    This function closes the session and deletes the session variables.
    """
    logout_user()
    session.pop('username', None)
    session.pop('current_access', None)
    session.pop('last_access', None)
    session.pop('entry_time', None)
    session.pop('last_activity', None)
    session.pop('user_folder', None)
    session.pop('topographical_file', None)
    session.pop('config_file', None)
    session.pop('symbols_file', None)
    session.pop('files_folder', None)
    session.pop('new_file_folder', None)


def create_user_folder():
    """
    This function creates, from each uploaded topographical data file name,
    a customized directory for each user.
    """
    new_file_folder = str(time.time())
    # Separate extension file name
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
