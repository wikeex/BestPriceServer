from . import db


class AccessToken(db.Model):
    __tablename__ = 'token'
    token = db.Column(db.TEXT, nullable=False)
    expires_at = db.Column(db.FLOAT, nullable=False)


class Keywords(db.Model):
    __tablename__ = 'user'
    open_id = db.Column(db.TEXT, nullable=False)
    keyword = db.Column(db.TEXT, nullable=False)
    insert_time = db.Column(db.FLOAT, nullable=False)


