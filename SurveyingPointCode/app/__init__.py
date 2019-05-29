"""
 SurveyingPointCode
 Copyright © 2018-2019 J. Eduardo Risco

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.txt>.
"""

# __init__.py
# File init
#
# Required Flask . BSD Licence. Copyright © 2010 by the Pallets team
# Required flask-login . MIT Licence. Copyright © 2011 Matthew Frazier
# Required SQLAlchemy.  MIT Licence. Copyright © 2005-2019 Michael Bayer and contributors.

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.login_message = 'You must be logged in to access this page.'
login_manager.login_view = '/login'
login_manager.init_app(app)

db = SQLAlchemy(app)
from app import route, models
