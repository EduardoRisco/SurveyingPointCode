from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

import os

POSTGRES = {
    'user': 'tfg',
    'pw': 'f04f1b4d7734f0dc3c4da46f19c0a9f49b56',
    'db': 'tfg',
    'host': '172.18.0.2',
    'port': '5432',
}

UPLOAD_FOLDER = os.path.abspath("./tmp/")
app = Flask(__name__)
app.config.from_object(Config)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.login_message = "You must be logged in to access this page."
login_manager.login_view = "/login"
login_manager.init_app(app)



app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db = SQLAlchemy(app)

from app import route,models
