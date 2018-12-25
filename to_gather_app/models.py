import time
import datetime
from . import db
from .exceptions import ActivityError
import werkzeug.http
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, jsonify, request
from functools import wraps

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    std_num = db.Column(db.String(11), unique=True)

    @classmethod
    def init(cls, _data):
        usr = cls.query.filter_by(std_num=_data.get("std_num")).first()
        if usr is not None:
            return usr
        new_user = cls(name = _data.get("username"),
                        std_num = _data.get("std_num"))
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def generate_token(self):
        s = Serializer("muxiniubi", expires_in=99999999)
        return s.dumps({'std_num': self.std_num,
                        'confirm': self.id}).decode('utf-8')

    def check(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not 'token' in request.headers:
                return jsonify({"msg": "no token attribution"}), 401
            usr = None
            t = request.headers['token'].encode('utf-8')
            s = Serializer("muxiniubi")
            try:
                _data = s.loads(t)
            except:
                return jsonify({"msg": "load token fail"}), 401
            uid = _data.get('confirm')
            unum = _data.get('std_num')
            print (uid, unum)
            if (uid is None) or (unum is None):
                return jsonify({"msg": "invalid token"}), 401
            return f({"id": uid, "unum": unum}, *args, **kwargs)
        return decorated_function

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    date = db.Column(db.Date)
    time = db.Column(db.String(40))
    event = db.Column(db.String(120))
    location = db.Column(db.String(60))
    tel = db.Column(db.String(13))
    qq = db.Column(db.String(12))
    question = db.Column(db.String(120))
    pickable = db.Column(db.Boolean, default=True)
    close = db.Column(db.Boolean, default=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    picker_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @classmethod
    def init(cls, _data, _info):
        _date = datetime.date(_data.get("year"),
                             _data.get("month"),
                             _data.get("day"))
        new_activity = cls(date = _date,
                           time = _data.get("time"),
                           location = _data.get("location"),
                           event = _data.get("event"),
                           question = _data.get("question"),
                           tel = _data.get("tel"),
                           qq = _data.get("qq"),
                           poster_id = _info.get("id"))
        db.session.add(new_activity)
        db.session.commit()
        return new_activity

    def getinfo(self):
        _rv = {
                  "aid": self.id,
                  "date": str(self.date),
                  "time": self.time,
                  "event": self.event,
                  "location": self.location,
                  "question": self.question,
                  "qq": self.qq,
                  "tel": self.tel,
                  "statu": {
                      "pickable": self.pickable,
                      "close": self.close
                  }
              }
        return _rv

    def setinfo(self, value):
        try:
            value = int(value)
        except:
            raise ActivityError
        if self.picker_id is not None:
            return
        self.picker_id = value
        self.waiting = False
        db.session.add(self)
        record = Picker2Activity.query.filter_by(picker_id = value, aid = self.id).first()
        if record is None:
            raise ActivityError
        record.fail = False
        record.waiting = False
        db.session.add(record)
        db.session.commit()

    def delinfo(self):
        if not self.close:
            raise ActivityError
        try:
            db.engine.execute("<SET FOREIGN_KEY_CHECKS=0>")
            db.session.delete(self)
            db.session.commit()
        except:
            pass

    info = property(getinfo, setinfo, delinfo, "I am information")

class Picker2Activity(db.Model):
    __tablename__ = "picker2activities"
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(120))
    picker_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    aid = db.Column(db.Integer, db.ForeignKey("activities.id"))
    waiting = db.Column(db.Boolean, default=True)
    fail = db.Column(db.Boolean, default=True)

    def getFail(self):
        return self.fail
    def setFail(self, value):
        self.waiting = False
        self.fail = value
        db.session.add(self)
        db.session.commit()

    FAIL = property(getFail, setFail)

    @classmethod
    def init(cls, aid, uid, ans):
        record = cls.query.filter_by(aid=aid, picker_id=uid).first()
        if record is not None:
            return 
        new_record = cls(aid=aid, picker_id=uid, answer=ans)
        db.session.add(new_record)
        db.session.commit()
        return

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(40))
    # time here to use werkzeug.http.http_date string
    readed = db.Column(db.Boolean, default=False)
    aid = db.Column(db.Integer, db.ForeignKey("activities.id"))
    picker_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    answer = db.Column(db.String(120))

    @classmethod
    def init(cls, aid, uid, ans):
        msg = cls(aid = aid, picker_id = uid, answer = ans)
        msg.time = werkzeug.http.http_date(time.time())
        db.session.add(msg)
        db.session.commit()
        Picker2Activity.init(aid, uid, ans)
        return msg
