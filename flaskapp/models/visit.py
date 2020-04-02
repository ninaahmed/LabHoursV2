from flaskapp import db

class Visit(db.Model):
    __tablename__ = "visits"
    id = db.Column(db.Integer, primary_key=True)
    eid = db.Column(db.String(10))
    time_entered = db.Column(db.DateTime, index=True, nullable=False)
    time_left = db.Column(db.DateTime)
    was_helped = db.Column(db.Integer)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))

