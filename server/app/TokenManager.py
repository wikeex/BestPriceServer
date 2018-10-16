

class TokenManager:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app
        config = app.config
        self.appid = config.get('APP_ID')
        self.secret = config.get('APP_SECRET')
