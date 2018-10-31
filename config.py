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
    SPIDER_DATABASE_URI = ''
    SPIDER_DATABASE_PORT = 27017
    SPIDER_DATABASE_USERNAME = ''
    SPIDER_DATABASE_PASSWORD = ''
    SPIDER_DATABASE_AUTH_SOURCE = ''
    SPIDER_DATABASE_AUTH_MECHANISM = ''

    # 用户数据库设置
    DATABASE_PATH = os.path.join(base_dir, 'data.sqlite3')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

    # 微信公众号设置
    WECHAT_DOMAIM = ''
    WECHAT_TOKEN = ''
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
        app.logger.addHandler(handler)


class TestingConfig(Config):
    TESTING = True

    # 产品数据库设置
    MONGO_HOST = ''
    DATABASE_PORT = 27017
    MONGO_DBNAME = ''
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''
    DATABASE_AUTH_SOURCE = ''

    # 用户数据库设置
    DATABASE_PATH = os.path.join(base_dir, 'data.sqlite3')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

    # 微信公众号设置
    WECHAT_DOMAIM = ''
    WECHAT_TOKEN = ''
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
    DATABASE_PATH = os.path.join(base_dir, 'data.sqlite3')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

    # 微信公众号设置
    WECHAT_TOKEN = ''
    WECHAT_DOMAIM = ''
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
        app.logger.addLevel(logging.INFO)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}


