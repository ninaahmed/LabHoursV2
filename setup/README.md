# Running the Lab Hours Queue Flask App


1. First, create a virtual environment: `$ python3 -m venv venv`

2. Activate the virtual environment:

    Mac/Linux: `$ source venv/bin/activate`

    Windows: `$ venv\Scripts\activate`

3. Install required packages: `(venv) $ pip3 install -r requirements.pip`

4. Create the required files which aren't included as a part of the repo. See "Missing Files"

5. Run the app! `(venv) $ flask run`

6. To deactive the virtual environment, run: `(venv) $ deactivate`

## Missing Files

There are some files required to run the application which are not included as a part of the repository for mostly obvious security reasons.

The most important file needed is the `flaskapp/config.cfg` which defines many configuration variables
for the application. Some of these include the application secret key, email server information,
etc. A template of the config file is provided in `setup/config.cfg` which for development purposes
can simply be copied to `flaskapp/config.cfg` (the template values are sufficient).

Then, a `labhours.db` SQLite database file will be needed to
handle instructor login and visit logging.
An empty database with the same schema is provided called `empty.db` and can be copied to `labhours.db`.
You can then use the provided database manipulation scripts
(`edit_instructors.py` and `edit_visits.py` to add to the tables).

A sample `zoomlinks.txt` file is provided, although you
may want to change its contents for testing.
