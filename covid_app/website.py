from os import getenv
from shutil import copyfile

from flask import Flask, request
from flask import render_template
from covid_app.controllers.database_helpers import connect_to_database
from covid_app.controllers.database_helpers import close_conection_to_database
from covid_app.controllers.database_helpers import change_database
from covid_app.controllers.database_helpers import query_database
from covid_app.controllers.database_helpers import query_names
#from tabulate import tabulate

app = Flask(__name__)

# This is a terrible example of how to configure a flask.
# this type of configuration should be done in a separate file,
# using environment variables. The code is written this way for
# relative ease of reading - but the code gets out of hand very
# quickly if you follow this approach.

# local file for testing purposes
app.config['DATABASE_FILE'] = 'covid_app/data/covid_app.sqlite'



# hack to run with sqlite on app engine: if the code is run on app engine,
# this will copy the existing database to a writeable tmp directory.
# note that it will get overwritten every time you deploy! a production-ready
# approach is to store the file long-term on google cloud storage,
# or, better yet, use fully managed  relational database management software
# via Cloud SQL.
if getenv('GAE_ENV', '').startswith('standard'):
    app_engine_path = "/tmp/covid_app.sqlite"
    copyfile(app.config['DATABASE_FILE'], app_engine_path)
    app.config['DATABASE_FILE'] = app_engine_path
else:
    pass


@app.route('/')
def index():
    # connect to the database with the filename configured above
    # returning a 2-tuple that contains a connection and cursor object
    # --> see file database_helpers for more
    
    database_tuple = connect_to_database(app.config["DATABASE_FILE"])
    # sql_query_names = "SELECT name FROM contacts"
    # names = query_database(database_tuple[1], sql_query_names)
    # names = [name[0] for name in names]
    names = query_names(database_tuple[1])

    sql_query = """SELECT date(meeting_date), contacts.name 
    FROM meetings 
    JOIN contacts ON meetings.contact_id=contacts.contact_id 
    WHERE meeting_date<=date('now') and meeting_date>=date('now','-14 days')
    ORDER BY date(meeting_date) DESC;"""

    meetings = query_database(database_tuple[1], sql_query)
    return render_template('index.html', names=names, meetings=meetings, page_title="Covid Diary")


@app.route('/create', methods=['POST'])
def create_meeting():
    try:
        name = request.form.get('name')
        phone_nb = request.form.get('phone_nb')
        address = request.form.get('address')
        e_mail = request.form.get('e-mail')
        # app.logger.info(name)
        # turn this into an SQL command. For example:
        # "Adam" --> "INSERT INTO Meetings (name) VALUES("Adam");"
        
        sql_insert_contact = "INSERT INTO contacts (name, phone_nb, address, e_mail) VALUES (\"{name}\",\"{phone_nb}\",\"{address}\",\"{e_mail}\");".format(
            name=name, phone_nb=phone_nb, address=address,e_mail=e_mail)
        print(sql_insert_contact)

        
        meeting_date = request.form.get('meeting_date')
        contact = request.form.get('contacts')
        print(meeting_date, contact)
        
        sql_query_contact_id = "SELECT contact_id FROM contacts WHERE name = (\"{contact}\")".format(contact=contact)
        print(sql_query_contact_id)


        database_tuple = connect_to_database(app.config["DATABASE_FILE"])
        
        # now that we have connected, add the new meeting (insert a row)
        # --> see file database_helpers for more  
        if name!=None:
            change_database(database_tuple[0], database_tuple[1], sql_insert_contact)

        elif meeting_date!=None and contact!=None:
            contact_id = query_database(database_tuple[1], sql_query_contact_id)
            contact_id = int(contact_id[0][0])
            print(contact_id)
        
            sql_insert_meeting = "INSERT INTO meetings (meeting_date, contact_id) VALUES (\"{meeting_date}\",\"{contact_id}\");".format(meeting_date=meeting_date,contact_id=contact_id)
            print(sql_insert_meeting)

            change_database(database_tuple[0], database_tuple[1], sql_insert_meeting)

        # now, get all of the meetings from the database, not just the new one.
        # first, define the query to get all meetings:

        sql_query = """SELECT date(meeting_date), contacts.name 
        FROM meetings 
        JOIN contacts ON meetings.contact_id=contacts.contact_id 
        WHERE meeting_date<=date('now') and meeting_date>=date('now','-14 days')
        ORDER BY date(meeting_date) DESC;"""


        # query the database, by passinng the database cursor and query,
        # we expect a list of tuples corresponding to all rows in the database
        meetings = query_database(database_tuple[1], sql_query)
        print(meetings)
        # meetings_table = tabulate(meetings, headers=["Name","Date"], showindex="Always", tablefmt="html")


        
        names = query_names(database_tuple[1])

        close_conection_to_database(database_tuple[0])

        # In addition to HTML, we will respond with an HTTP Status code
        # The status code 201 means "created": a row was added to the database
        return render_template('index.html', page_title="Covid Diary",
                                meetings=meetings, names=names), 201
    except Exception:
        # something bad happended. Return an error page and a 500 error
        error_code = 500
        return render_template('error.html', page_title=error_code), error_code


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
