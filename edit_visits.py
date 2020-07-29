from flaskapp import db
from flaskapp.models.visit import Visit
import csv
import os

"""
    A utility script for manipulating the visits
    table in the database. 

    This is not used by the app itself, it is a 
    utility for use by those maintaining the app 
    and database.
"""
def display_menu():

    VIEW_NUM_ENTRIES = 1
    EXPORT_CSV = 2
    DELETE_ALL = 3
    SAVE_EXIT = 4
    NO_SAVE_EXIT = 5

    choice = 0
    while choice != SAVE_EXIT and choice != NO_SAVE_EXIT:
        if choice == VIEW_NUM_ENTRIES:
            num_entries = len(Visit.query.all())
            print(f"There are {num_entries} entries in the visits table.")
            choice = 0 
        elif choice == EXPORT_CSV:
            export_csv()
            choice = 0
        elif choice == DELETE_ALL:
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
            print(f"{VIEW_NUM_ENTRIES}: View number of entries in visits table")
            print(f"{EXPORT_CSV}: Export to CSV")
            print(f"{DELETE_ALL}: Delete all entries in visits table")
            print(f"{SAVE_EXIT}: Write changes to database and exit")
            print(f"{NO_SAVE_EXIT}: Exit without writing to database")
            choice = int(input("Select an option: "))
    if choice == SAVE_EXIT:
        db.session.commit()
    exit()

def export_csv():
    print_divide()
    file_name = input("Enter output file name: ")
    if os.path.isfile(file_name):
        proceed = input(f" {file_name} already exists, overwrite it? (y/n): ").lower().strip()
        if proceed != 'y':
            return
    try:
        output_file = open(file_name, 'w')
        outcsv = csv.writer(output_file, quotechar=',')
        outcsv.writerow(['id', 'eid', 'time_entered', 'time_left', 'was_helped', 'instructor_id'])
        visits = Visit.query.all()
        for visit in visits:
            outcsv.writerow([visit.id, visit.eid, visit.time_entered, visit.time_left, visit.was_helped, visit.instructor_id])
        output_file.close()
        print("Export successful")
    except Exception as e:
        print("An error occurred")
        print(e)
    return

def print_divide():
    print()
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

if __name__ == "__main__":
    display_menu()
