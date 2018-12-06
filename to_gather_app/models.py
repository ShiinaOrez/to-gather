import werkzeug.http
import time
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimeJSONWebSignatureSerializer as Serializer
from flask import current_app

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    std_num = db.Column(db.String(11), unique=True)

    def generate_confirmation_token(self, expiration=99999999):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'std_num': self.std_num,
                        'confirm': self.id}).decode('utf-8')

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, unique=True)
    date = db.Column(db.Date)
    time = db.Column(db.String(40))
    event = db.Column(db.String(120))
    location = db.Column(db.String(60))
    question = db.Column(db.String120)
    pickable = db.Column(db.Bool, default=True)
    close = db.Column(db.Bool, default=False)
    poster_id = db.Column

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        _rv = {
                  "aid": self.id,
                  "date": str(self.date),
                  "time": self.time,
                  "event": self.event,
                  "location": self.location,
              }
        return _rv

    def __set__(self, obj, value):
        if value not in ("pick", "close"):
            raise ActivityError
        if value is "pick":
            if self.pickable:
                self.pickable = False
            else:
                raise ActivityError
        if value is "close":
            if not self.close:
                self.close = True
        db.session.add(self)
        db.session.commit()