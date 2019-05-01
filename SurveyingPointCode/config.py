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
