import uuid

class Student:
    def __init__(self, name, email, eid, uid):
        self.name = name
        self.email = email
        self.eid = eid
        self.id = str(uid)