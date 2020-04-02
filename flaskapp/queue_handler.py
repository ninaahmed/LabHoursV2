from threading import Lock
from flaskapp.student import Student

queue_lock = Lock()

student_queue = []

def enqueue(name, email, eid):
	added_person = Student(name, email, eid)

	# check to see if they are in the queue already
	remove(eid)
	
	#add them to the queue, return their place in line
	student_queue.append(added_person)
	return len(student_queue)

def get_students():
	return student_queue

def remove(eid):
	for i in range(0, len(student_queue)):
		if(eid == student_queue[i].eid):
			del student_queue[i]
			break
