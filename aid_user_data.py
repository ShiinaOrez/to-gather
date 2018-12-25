from to_gather_app import db
from to_gather_app.models import Message, Picker2Activity


count = 0
records = Picker2Activity.query.filter_by(fail=True, waiting=False).all()
print (len(records))
for record in records:
    aid = record.aid
    pid = record.picker_id
    msg = Message.query.filter_by(aid=aid, picker_id=pid, readed=True).first()
    if msg is not None:
        msg.readed = False
        db.session.add(msg)
        count += 1
db.session.commit()
print("Fixed Record:", count, "records")
