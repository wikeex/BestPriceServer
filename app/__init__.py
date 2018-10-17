from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from config import config
from .TokenManager import TokenManager

db = SQLAlchemy()
tokenmanager = TokenManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    db.init_app(app)
    tokenmanager.init_app(app)

    from .wechat import wechat as wechat_blueprint
    app.register_blueprint(wechat_blueprint)

    return app





