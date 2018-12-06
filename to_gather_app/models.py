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
    poster_id = db.Column

    def __get__(self):
        
