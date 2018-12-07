import datetime
from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import User, Activity, Message

require = ("year", "month", "day", "location", "event", "question", "time")

@api.route("/activity/post/", methods=["POST"], endpoint="ActivityPost")
@User.check
def activity_post(info):
    for key in require:
        if key not in request.values.keys():
            return jsonify("msg": "payload invalid"), 402
    post_date = datetime.date(int(request.values.get("year")),
                              int(request.values.get("month")),
                              int(request.values.get("day"))
    if post_date < datetime.date():
        return jsonify({"msg": "date invalid"}), 405
    act = Activity.init(request.values, info)
    return jsonify({"activityID": act.id}), 200

@api.route("/activity/<int:aid>/", methods=["GET", "POST", "PUT"], endpoint="ActivityEntity")
@User.check
def activity_entity(info):
    if request.method == "GET":
        act = Activity.query.filter_by(id=request.values.get('aid')).first()
        
