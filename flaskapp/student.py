import uuid
"""
    Class to represent a Student entry in the
    Lab Hours Queue.
"""
class Student:
    def __init__(self, name, email, eid, uid):
        self.name = name
        self.email = email
        self.eid = eid
        # Corresponds to the id of the visit entry
        # which was created when this student joined
        # the queue.
        self.id = str(uid)