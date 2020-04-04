from flaskapp import db
from flaskapp.models.visit import Visit

def display_menu():
    choice = 0
    while choice != 3 or choice != 4:
        if choice == 1:
            num_entries = len(Visit.query.all())
            print(f"There are {num_entries} entries in the visits table.")
            choice = 0 
        if choice == 2:
            all_visits = Visit.query.all()
            num_entries = len(all_visits)
            print(f"Are you sure you want to delete all {num_entries} entries in the visits table?")
            proceed = input("(y/n): ")
            if proceed.lower() == 'y':
                db.session.query(Visit).delete()
            choice = 0
        else:
            print_divide()
            print("Visits table editor")
            print("1: View number of entries in visits table")
            print("2: Delete all entries in visits table")
            print("3: Write changes and exit")
            print("4: Exit without writing")
            choice = int(input("Select an option: "))
    if choice == 3:
        db.session.commit()
    exit()

def print_divide():
    print()
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

if __name__ == "__main__":
    display_menu()