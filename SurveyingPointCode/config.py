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

# config.py
# Module containing the configuration of application
import os

from app.cad_utilities import cad_colors_palette, cad_versions

basedir = os.path.abspath(os.path.dirname(__file__))
POSTGRES = {
    'user': os.environ.get("POSTGRES_USER"),
    'pw': os.environ.get("POSTGRES_PASS"),
    'db': os.environ.get("POSTGRES_DBNAME"),
    'host': os.environ.get("POSTGRES_HOST"),
    'port': os.environ.get("POSTGRES_PORT")
}


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.abspath('./tmp/')
    CAD_VERSIONS = cad_versions
    CAD_COLORS = cad_colors_palette
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
