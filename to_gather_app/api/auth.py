from flask import jsonify, request, current_app
from . import api
from .. import db
from ..models import User, Activity, Message
from ..verify import try_ccnu

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimeJSONWebSignatureSerializer as Serializer

@api.route('/auth/login/', methods = ['GET'], endpoint="Login")
def login():
    jv = request.get_json()
    is_student = try_ccnu(username = jv.get("std_num"),
                          password = jv.get("password"))
    if not is_student:
        return jsonify({"msg": "login fail"}), 401
    usr = User.init(request.values)
    token = usr.generate_token()
    return jsonify({"token": token,
                    "username": usr.username,
                    "std_num": usr.std_num}), 200