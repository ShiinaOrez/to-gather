import datetime
from flask import jsonify, request, current_app
from . import api
from .. import db
from ..models import User, Activity, Message, Picker2Activity
from ..exceptions import ActivityError
from .._internal import _get_records

require = ("year", "month", "day", "location", "event", "question", "tel", "qq", "time")

@api.route("/activity/post/", methods=["POST"], endpoint="ActivityPost")
@User.check
def activity_post(info):
    for key in require:
        if request.json.get(key) is None:
            return jsonify({"msg": "payload invalid"}), 402
    post_date = datetime.date(int(request.json.get("year")),
                              int(request.json.get("month")),
                              int(request.json.get("day")))
    if post_date < datetime.date.today():
        return jsonify({"msg": "date invalid"}), 405
    act = Activity.init(request.json, info)
    return jsonify({"activityID": act.id}), 200

@api.route("/activity/<int:aid>/", methods=["GET", "POST", "PUT"], endpoint="ActivityEntity")
@User.check
def activity_entity(info, aid):
    act = Activity.query.filter_by(id=aid).first()
    if act is None:
        return jsonify({"msg": "activity not existed"}), 406

    if request.method == "GET":
        if act.date < datetime.date.today():
            act.close = True
            del act.info
        if act.close:
            return jsonify({"msg": "activity is closed"}), 403
        return jsonify(act.info), 200
    
    if request.method == "POST":
        if info.get("id") == act.poster_id:
            return jsonify({"msg": "can't pick your self"}), 407
        record = Picker2Activity.query.filter_by(picker_id=info.get("id"), aid=aid).first()
        if record is not None:
            return jsonify({"msg": "already pick it before"}), 402
        if act.close:
            return jsonify({"msg": "activity is closed"}), 403
        if not act.pickable:
            return jsonify({"msg": "pick is over"}), 405
        msg = Message.init(aid, info.get("id"), request.get_json().get("answer"))
        return jsonify({"msg": "pick successful"}), 200
    
    if request.method == "PUT":
        if info.get("id") == request.json.get("pickerID"):
            return jsonify({"msg": "can't pick your self"}), 407
        if act.close:
            return jsonify({"msg": "activity is closed"}), 403
        if not act.pickable:
            return jsonify({"msg": "pick is over"}), 405
        if not request.json.get("atti"):
            record = Picker2Activity.query.filter_by(aid=aid, picker_id=request.json.get("pickerID")).first()
            record.FAIL = True
            return jsonify({"msg": "pick be refused"}), 201
        if act.poster_id != info.get("id"):
            return jsonify({"msg": "please modify your self activity"}), 401
        try:
            act.info = request.json.get("pickerID")
        except ActivityError:
            return jsonify({"msg": "picking error"}), 405
        else:
            records = Picker2Activity.query.filter_by(aid=aid).all()
            for record in records:
                if record.waiting:
                    record.waiting = False
                    record.fail = True
                    db.session.add(record)
            db.session.commit()
        return jsonify({"msg": "picking is over!"}), 200       

@api.route("/activity/pickable/list/", methods=["GET"], endpoint="PickableList")
def pickable_list():
    page = request.args.get("page")
    _data = _get_records(Activity, Activity.pickable, True, page)
    if _data["rowsNum"] == 0:
        return jsonify({"msg": "none activity"}), 201
    data = []
    for activity in _data["activityList"]:
        data.append({
            "activityID": activity.id,
            "datetime": str(activity.date) + " " + activity.time,
            "event": activity.event
        })
    _data["activityList"] = data
    return jsonify(_data), 200

@api.route("/user/<string:unum>/post-activities/list/", methods=["GET"], endpoint="PostList")
@User.check
def post_list(info, unum):
    page = request.args.get("page")
    usr = User.query.filter_by(std_num=unum).first()
    if usr is None: 
        return jsonify({"msg": "user not existed!"}), 406
    if usr.id != info.get("id"):
        return jsonify({"msg": "please check your self information"}), 407
    _data = _get_records(Activity, Activity.poster_id, usr.id, page)
    if _data["rowsNum"] == 0:
        return jsonify({"msg": "you have posted nothing"}), 201
    data = []
    for activity in _data["activityList"]:
        hasMessages = True
        msgs = Message.query.filter_by(aid=activity.id, readed=False).all()
        if msgs is None or []:
            hasMessages = False
        data.append({
            "activityID": activity.id,
            "datetime": str(activity.date) + " " + activity.time,
            "event": activity.event,
            "close": activity.close,
            "hasMessage": hasMessages
        })
    _data["activityList"] = data
    return jsonify(_data), 200

@api.route("/user/<string:unum>/pick-activities/list/", methods=["GET"], endpoint="PickList")
@User.check
def pick_list(info, unum):
    page = request.args.get("page")
    usr = User.query.filter_by(std_num=unum).first()
    if usr is None: 
        return jsonify({"msg": "user not existed!"}), 406
    if usr.id != info.get("id"):
        return jsonify({"msg": "please check your self information"}), 407
    _data = _get_records(Picker2Activity, Picker2Activity.picker_id, usr.id, page)
    if _data["rowsNum"] == 0:
        return jsonify({"msg": "you have picked nothing"}), 201
    data = []
    for record in _data["activityList"]:
        if record.waiting:
            statu = 0
        elif record.fail:
            statu = 2
        else:
            statu = 1
        activity = Activity.query.filter_by(id=record.aid).first()
        data.append({
            "activityID": activity.id,
            "datetime": str(activity.date) + " " + activity.time,
            "event": activity.event,
            "statu": statu
        })
    _data["activityList"] = data
    return jsonify(_data), 200
