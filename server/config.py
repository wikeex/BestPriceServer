import os
from time import strftime, localtime, time

base_dir = os.path.abspath(os.path.dirname(__name__))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        ...


class DevelopmentConfig(Config):
    DEBUG = True
    # 日志文件位置
    LOG_DIR = os.path.join(base_dir, 'logs')
    LOG_FILENAME = 'logger-' + strftime('%Y-%m-%d', localtime(time())) + '.log'

    # 产品数据库设置
    MONGO_HOST = ''
    DATABASE_PORT = 27017
    MONGO_DBNAME = ''
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''
    DATABASE_AUTH_SOURCE = ''

    # 用户数据库设置
    SQLALCHEMY_DATABASE_URI = ''

    # 微信公众号设置
    TOKEN = ''
    APP_ID = ''
    APP_SECRET = ''
    MODEL_ID = ''

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging

        handler = logging.FileHandler(os.path.join(cls.LOG_DIR, cls.LOG_FILENAME), encoding='UTF-8')
        log_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
        )
        handler.setFormatter(log_format)
        app.logger.setLevel(logging.DEBUG)
        app.logger.setHandler(handler)


class TestingConfig(Config):
    # 产品数据库设置
    MONGO_HOST = ''
    DATABASE_PORT = 27017
    MONGO_DBNAME = ''
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''
    DATABASE_AUTH_SOURCE = ''

    # 用户数据库设置
    SQLALCHEMY_DATABASE_URI = ''

    # 微信公众号设置
    TOKEN = ''
    APP_ID = ''
    APP_SECRET = ''
    MODEL_ID = ''


class ProductionConfig(Config):
    # 日志文件
    LOG_DIR = os.path.join(base_dir, 'logs')
    LOG_FILENAME = 'logger-' + strftime('%Y-%m-%d', localtime(time())) + '.log'

    # 产品数据库设置
    MONGO_HOST = ''
    DATABASE_PORT = 27017
    MONGO_DBNAME = ''
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''
    DATABASE_AUTH_SOURCE = ''

    # 用户数据库设置
    SQLALCHEMY_DATABASE_URI = ''

    # 微信公众号设置
    TOKEN = ''
    APP_ID = ''
    APP_SECRET = ''
    MODEL_ID = ''

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging

        handler = logging.FileHandler(os.path.join(cls.LOG_DIR, cls.LOG_FILENAME), 'UTF-8')
        log_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
        )
        handler.setFormatter(log_format)
        app.logger.setHandler(handler)
        app.logger.setLevel(logging.INFO)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}


