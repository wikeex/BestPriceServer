import time
import requests
import sqlite3


class TokenManager:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    @classmethod
    def get_access_token(cls):
        conn = sqlite3.connect(cls.app.config.get('SQLALCHEMY_DATABASE_URI'))
        cursor = conn.cursor()
        cursor.execute('SELECT access_token FROM user ORDER BY expires_in DESC LIMIT 1')
        try:
            access_token = cursor.fetchall()[0][0]
        except IndexError:
            access_token = None
        if access_token and access_token > time.time():
            conn.close()
            return access_token
        else:
            try:
                url = "https://api.weixin.qq.com/cgi-bin/token?"
                parameters = dict(
                    grant_type='client_credential',
                    appid=cls.appid,
                    secret=cls.secret
                )
                response = requests.get(url, params=parameters)
                access_token = response.json().get('access_token')
                expires_in = response.json().get('expires_in')
                cursor.execute(
                    'INSERT INTO user (access_token, expires_at) VALUES (?, ?)', (access_token, expires_in+time.time())
                )
                conn.commit()
                conn.close()
                return access_token
            except TimeoutError as e:
                ...

    @classmethod
    def init_app(cls, app):
        cls.app = app
        config = app.config
        cls.appid = config.get('APP_ID')
        cls.secret = config.get('APP_SECRET')
