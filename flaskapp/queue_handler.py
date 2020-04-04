from threading import Lock
from flaskapp.student import Student

"""
	Representation of the Queue in memory. This
	is a list of Student objects where index=0 is the
	"front" of the queue.
"""
student_queue = []

"""
	Enqueues a Student object to the end of the queue.
	If the students was already in the queue, based on
	EID, then their previous entry is removed and they are
	added to the end of the queue.
"""
def enqueue(student):
	# check to see if they are in the queue already
	remove_eid(student.eid)
	
	#add them to the queue, return their place in line
	student_queue.append(student)
	return len(student_queue)

"""
	Returns the list of students so that it
	can be printed out on the View Queue page.
"""
def get_students():
	return student_queue

"""
	Returns the "runner-up" Student object.
	This is the student which is after the first person
	in line.
"""
def peek_runner_up():
	if len(student_queue) <= 1:
		return None
	return student_queue[1]

"""
	Removes a student based on a unique Visit ID.
	This ID is assigned when the student is added to the
	queue and their "visit" is added to the visits table.
	This ID is entirely sequential and thus students should NEVER
	be allowed to remove themselves based on this ID.
"""
def remove(id):
	for i in range(0, len(student_queue)):
		if(id == student_queue[i].id):
			del student_queue[i]
			break

"""
	Removes a student based on their UT EID that was
	entered when they joined the queue.
"""
def remove_eid(eid):
	for i in range(0, len(student_queue)):
		if(eid == student_queue[i].eid):
			s = student_queue[i]
			del student_queue[i]
			return s
	return None