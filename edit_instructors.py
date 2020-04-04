from flaskapp import db
from flaskapp.models.instructor import Instructor
from werkzeug.security import generate_password_hash

def display_menu():
    choice = 0
    while choice != 5 and choice != 6:
        if choice == 1:
            new_instructor()
            choice = 0
        elif choice == 2:
            modify_instructor()
            choice = 0
        elif choice == 3:
            delete_instructor()
            choice = 0
        elif choice == 4:
            list_instructors()
            choice = 0
        else:
            print_divide()
            print("Instructor table editor")
            print("1. Add a new instructor entry")
            print("2. Modify an instructor entry")
            print("3. Delete an instructor entry")
            print("4. List all instructor entries")
            print("5. Write changes and exit")
            print("6. Exit without writing")
            choice = int(input("Select an option: "))
    if choice == 5:
        db.session.commit()
    exit()

def new_instructor():
    print_divide()
    print("Creating a new instructor entry")
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    email = input("Email: ").strip()
    password = generate_password_hash(input("Password: ").strip())
    proceed = input("Add this instructor to the table? (y/n): ").strip()
    if proceed.lower() != 'y':
        return
    instr = Instructor(first_name = first_name, last_name = last_name, email=email, password_hash = password)
    db.session.add(instr)
    print(f"{first_name} has been added as an Instructor!")
    display_menu()
    
def modify_instructor():
    print_divide()
    print("Modify an instructor entry")
    email = input("Enter email of instructor to modify: ")
    instr = Instructor.query.filter_by(email=email).first()
    if instr is None:
        print("An instructor with that email does not exist.")
        return
    choice = input(f"Modify the entry for {instr.first_name} {instr.last_name} ? (y/n): ")
    if choice.lower().strip() != 'y':
        return
    print(f"Please enter the new information for {instr.first_name}. Leave empty if you would like to keep the existing value.")
    first_name = input(f"First name ({instr.first_name}): ").strip()
    last_name = input(f"Last name ({instr.last_name}): ").strip()
    email = input(f"Email ({instr.email}): ").strip()
    password = generate_password_hash(input("Password: ").strip())
    if not first_name:
        first_name = instr.first_name
    if not last_name:
        last_name = instr.last_name
    if not email:
        email = instr.email
    if not password:
        password = instr.password_hash
    proceed = input(f"Make these changes for {first_name}? (y/n): ")
    if proceed.lower() != 'y':
        return
    instr.first_name = first_name
    instr.last_name = last_name
    instr.email = email
    instr.password_hash = password

def delete_instructor():
    print_divide()
    email = input("Enter email of instructor to delete: ")
    instr = Instructor.query.filter_by(email=email).first()
    if instr is None:
        print("An instructor with that email does not exist.")
        return
    proceed = input(f"Delete the entry for {instr.first_name} {instr.last_name} ({instr.email})? (y/n): ")
    if proceed.lower() != 'y':
        return 
    db.session.delete(instr)

def list_instructors():
    print_divide()
    instructors = Instructor.query.all()
    print("All entries in the instructor table: ")
    for instr in instructors:
        print(f"{instr.first_name} {instr.last_name}, {instr.email}")

def print_divide():
    print()
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

if __name__=="__main__":
    display_menu()
