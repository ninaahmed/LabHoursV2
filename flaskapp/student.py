import uuid

class Student:
    def __init__(self, name, email, eid):
        self.name = name
        self.email = email
        self.eid = eid
        self.id = str(uuid.uuid4())