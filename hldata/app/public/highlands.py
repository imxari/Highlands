""" Imports """
from flask import Flask, render_template, url_for, redirect, flash, request, session, abort
import os
import sqlite3

""" Init the Flask application  """
app = Flask(__name__)
app.secret_key = os.urandom(2)

""" Dashboard Zerotier-One node information """
def dashboard_info():
    pass

# =============================================================================

""" Class for handling database connections, checks etc... """
class Database:

    """ Handles connect us to the database """
    dbpath = "/app/highlands.db"
    def connect(self):
        return sqlite3.connect(self.dbpath)

    """ Handles the initial setup of the sqlite3 database """
    def setup(self):
	user_table_sql = 'CREATE TABLE `users`( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `username` VARCHAR(75) NOT NULL, `password` VARCHAR(75) NOT NULL, `email` VARCHAR(75) NOT NULL)'
        #default_user_sql = 'INSERT INTO users(username, password, email) VALUES("admin", "password", "admin@invalid.com")'

	conn = self.connect()
	c = conn.cursor()

	c.execute(user_table_sql)
	#c.execute(default_user_sql)

        User().create("admin", "password", "example@invalid.com")

	conn.commit()
	conn.close()

    """ Handles initialization of the database """
    def __init__(self):
        if os.path.exists(self.dbpath) == False:
	    print "[?] Error, database wasn't found..."
	    self.setup()
	    print "[!] Done, database was created"

""" Class for handling database interactions related to Users """
class User:
    """ Handles creating a new user account """
    def create(self, username, password, email):
        if username == None or password == None or email == None:
	    return False
	else:
	    query = 'INSERT INTO users(username, password, email) VALUES("{user}", "{passw}", "{mail}")'.format(user=username, passw=password, mail=email)
	    conn = Database().connect()
	    c = conn.cursor()

	    try:
	        c.execute(query)
		conn.commit()
	    except sqlite3.Error as e:
	        print str(e)
		conn.close()
		return False
	    finally:
	        conn.close()
	        return True


    """ Handles checking the provided data for signing in a user """
    def login(self, POST_USERNAME, POST_PASSWORD):
        conn = Database().connect()

        c = conn.cursor()
	c.row_factory = sqlite3.Row
        c.execute("SELECT username,password FROM users WHERE username='{un}' AND password='{pw}'".format(un=POST_USERNAME, pw=POST_PASSWORD))
       
        usernameCorrect = False
	passwordCorrect = False

	dbresult = c.fetchone()

        if dbresult == None or len(dbresult) <= 0:
	    print "[!] User: " + POST_USERNAME + " has failed authentication! Possible break-in attempt?"
	    return False

	if POST_USERNAME == dbresult["username"]:
	    usernameCorrect = True
	if POST_PASSWORD == dbresult["password"]:
	    passwordCorrect = True

        if usernameCorrect == True and passwordCorrect == True:
	    print "[!] User: " + POST_USERNAME + " has been authenticated successfully!"
            return True
	else:
	    print "[!] User: " + POST_USERNAME + " has failed authentication! Possible break-in attempt?"
	    return False
 

# =============================================================================

""" Default route """
@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return login()

""" Dashboard """
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

""" Login check """
@app.route('/logincheck', methods=['POST'])
def logincheck():

    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    result = User().login(POST_USERNAME, POST_PASSWORD)

    if result:
        session['logged_in'] = True
        session['username'] = request.form['username']
        return dashboard()
    else:
        flash('Either your username or password was wrong. Try again.')
        return login()

# =============================================================================

""" Start the Flask application """
if __name__ == "__main__":
    Database()
    app.run(debug=True, host='0.0.0.0', port=5000)

