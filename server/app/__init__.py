from flask import Flask
from flask_werobot import WeRoBot
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from ..config import config

robot = WeRoBot()
db = SQLAlchemy()
mongo = PyMongo()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    robot.init_app(app)
    mongo.init_app(app)





