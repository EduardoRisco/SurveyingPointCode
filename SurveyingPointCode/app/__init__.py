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
