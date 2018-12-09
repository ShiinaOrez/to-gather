from flask import jsonify, request, current_app
from . import api
from .. import db
from ..models import User, Activity, Message
from ..verify import try_ccnu

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@api.route('/auth/login/', methods = ['POST'], endpoint="Login")
def login():
    jv = request.get_json()
    is_student = try_ccnu(username = jv.get("std_num"),
                          password = jv.get("password"))
    if not is_student:
        return jsonify({"msg": "login fail"}), 401
    usr = User.init(jv)
    token = usr.generate_token()
    return jsonify({"token": token,
                    "username": usr.name,
                    "std_num": usr.std_num}), 200
