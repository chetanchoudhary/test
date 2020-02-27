from db import db


class TemplateModel(db.Model):

    __tablename__ = "templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    format = db.Column(db.String(10))
    timeInterval = db.Column(db.Integer)
    frequency = db.Column(db.Integer)
    payload = db.Column(db.String(1000))

    def __init__(self, name, _format, timeInterval, frequency, payload):
        self.name = name
        self.format = _format
        self.timeInterval = timeInterval
        self.frequency = frequency
        self.payload = payload

    def json(self):
        return {"id": self.id, "name": self.name,"format": self.format, "timeInterval": self.timeInterval, "frequency": self.frequency, "payload": self.payload}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
