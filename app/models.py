from . import db, mongo


class AccessToken(db.Model):
    __tablename__ = 'token'
    token = db.Column(db.TEXT, nullable=False)
    expires_at = db.Column(db.FLOAT, nullable=False)


class Keywords(db.Model):
    __tablename__ = 'user'
    open_id = db.Column(db.TEXT, nullable=False)
    keyword = db.Column(db.TEXT, nullable=False)
    insert_time = db.Column(db.FLOAT, nullable=False)


class Values(mongo.Document):
    image_url = mongo.StringField()
    smzdm_url = mongo.StringField()
    title = mongo.StringField()
    insert_time = mongo.DateTimeField()
    price = mongo.FloatField()
    description = mongo.StringField()


class Item(mongo.Document):
    keyword = mongo.StringField()
    values = mongo.DocumentField(Values)
