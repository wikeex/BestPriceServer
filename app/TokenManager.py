import time
import requests
import sqlite3


class TokenManager:
    """
    该类用来维护微信的access_token，因为本服务只针对于一个微信公众号，所以设置该类所有实例共用类变量中的微信公众号信息。
    """
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    @classmethod
    def get_access_token(cls):
        """
        先在项目文件夹下链接sqlite3数据库，再从token表中查询token和expires_at列，如果没有token表则新建token表，
        并且从微信服务器获取access_token并存到数据库中。
        :return: 返回access_token
        """
        conn = sqlite3.connect(cls.app.config.get('DATABASE_PATH'))
        cursor = conn.cursor()

        try:
            # 查询token
            cursor.execute('SELECT token, expires_at FROM token ORDER BY expires_at DESC LIMIT 1')
            access_token = cursor.fetchall()[0][0]
            expires_at = cursor.fetchall()[0][1]
        except sqlite3.OperationalError:
            # 捕获error，新建table
            cursor.execute("""
            CREATE TABLE token (
              token TEXT NOT NULL,
              expires_at FLOAT NOT NULL
            );
            """)
            access_token = None
        except IndexError:
            access_token = None
        if access_token and expires_at > time.time():
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
                # 获取到的token存入数据库
                cursor.execute(
                    'INSERT INTO token (token, expires_at) VALUES (?, ?)', (access_token, expires_in+time.time())
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
        app.get_access_token = cls.get_access_token()
