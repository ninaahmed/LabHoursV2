from threading import Lock
from flaskapp.student import Student

queue_lock = Lock()

student_queue = []

def enqueue(student):

	# check to see if they are in the queue already
	remove(student.eid)
	
	#add them to the queue, return their place in line
	student_queue.append(student)
	return len(student_queue)

def get_students():
	return student_queue

def remove(id):
	for i in range(0, len(student_queue)):
		if(id == student_queue[i].id):
			del student_queue[i]
			break

def remove_eid(eid):
	for i in range(0, len(student_queue)):
		if(eid == student_queue[i].eid):
			del student_queue[i]
			return True
	return False