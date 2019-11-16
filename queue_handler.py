from threading import Lock
from student import Student

queue_lock = Lock()

student_queue = []

def add_to_queue(name, email, eid):
	added_person = Student(name, email, eid)

	# check to see if they are in the queue already
	for i in range(0, len(student_queue)):
		if(added_person == student_queue[i]):
			del student_queue[i]
	
	#add them to the queue, return their place in line
	student_queue.append(added_person)
	return len(student_queue) - 1

def get_students():
	return student_queue