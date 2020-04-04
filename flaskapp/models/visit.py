from flaskapp import db

"""
    Database model to represent a "Visit" in the "visits"
    table. A Visit is created anytime a student joins the
    queue. Unlike the queue itself, entries in the "visits"
    table are stored in the databse and persist even after
    the application is restarted.

    These entries in the visits table hold the eid of the student,
    The time they entered the line, the time they left (either
    as a result of being helped or removed), a flag indicating
    whether or not they were actually helped, and the id of the
    instructor who helped the student (left as NULL if the student
    was removed).

    If true anonymity is desired in keeping these statistics,
    then the eid column does not have to be used. It is not necessary
    to any other functionality.
"""
class Visit(db.Model):
    __tablename__ = "visits"
    id = db.Column(db.Integer, primary_key=True)
    eid = db.Column(db.String(10))
    time_entered = db.Column(db.DateTime, index=True, nullable=False)
    time_left = db.Column(db.DateTime)
    was_helped = db.Column(db.Integer)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'))

