import os

from app.cad_utilities import cad_colors_palette, cad_versions

basedir = os.path.abspath(os.path.dirname(__file__))
POSTGRES = {
    'user': 'postgres',
    'pw': 'cartometrix',
    'db': 'TFG1',
    'host': 'localhost',
    'port': '5433',
}

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.abspath('./tmp/')
    CAD_VERSIONS = cad_versions
    CAD_COLORS_PALETTE = cad_colors_palette
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
