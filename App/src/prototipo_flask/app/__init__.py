from flask import Flask
from config import Config
import os

UPLOAD_FOLDER = os.path.abspath("./tmp/")
app = Flask(__name__)
app.config.from_object(Config)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

from app import route
