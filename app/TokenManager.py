import time
import requests
from .models import AccessToken


class TokenManager:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    @classmethod
    def get_access_token(cls):
        access_token = AccessToken.query.order_by(AccessToken.expires_at.desc()).first()
        if access_token.expires_at > time.time():
            return access_token.token
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
                AccessToken(token=access_token, expires_at=expires_in + time.time())
                return access_token
            except TimeoutError as e:
                ...

    @classmethod
    def init_app(cls, app):
        cls.app = app
        config = app.config
        cls.appid = config.get('APP_ID')
        cls.secret = config.get('APP_SECRET')
