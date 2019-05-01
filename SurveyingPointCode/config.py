import os

from app.cad_utilities import cad_colors_palette, cad_versions

basedir = os.path.abspath(os.path.dirname(__file__))
POSTGRES = {
    'user': 'tfg',
    'pw': 'f04f1b4d7734f0dc3c4da46f19c0a9f49b56',
    'db': 'tfg',
    'host': 'postgis',
    'port': '5432'
}


class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.abspath('./tmp/')
    CAD_VERSIONS = cad_versions
    CAD_COLORS = cad_colors_palette
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
