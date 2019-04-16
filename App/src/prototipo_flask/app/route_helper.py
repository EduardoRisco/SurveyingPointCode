# -*- coding: utf-8 -*-
#
# Module containing auxilary functions associated with route.py
#
# J. Eduardo Risco 16-04-2019
#

import os
import time
from datetime import datetime, timedelta

from flask import make_response, render_template, request, session
from flask_login import logout_user
from werkzeug.utils import secure_filename

from app import app

def add_session(user):
    '''
    This function adds variables to the user session.
    '''    
    session['username'] = user.username
    session['current_access'] = datetime.now()
    session['last_access'] = user.last_access
    session['entry_time'] = str(time.time())
    session['last_activity'] = time.time()

def user_logout():
    '''
    This function closes the session and deletes the session variables.
    '''    
    logout_user()
    session.pop('username', None)
    session.pop('current_access', None)
    session.pop('last_access', None)    
    session.pop('entry_time', None)
    session.pop('last_activity', None)