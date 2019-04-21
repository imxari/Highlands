""" Imports """
from flask import Flask, render_template, url_for, redirect, flash, request, session, abort
import os
import sqlite3
import hashlib

""" Init the Flask application  """
app = Flask(__name__)
app.secret_key = os.urandom(2)

""" Class for handling database connections, checks etc... """
class Database:
    dbpath = "/app/highlands.db"
    def connect(self):
        return sqlite3.connect(self.dbpath)

    def setup(self):
	user_table_sql = 'CREATE TABLE `users`( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `username` VARCHAR(75) NOT NULL, `password` VARCHAR(75) NOT NULL, `firstname` VARCHAR(75) NOT NULL, `lastname` VARCHAR(75) NOT NULL, `email` VARCHAR(75) NOT NULL)'
        default_user_sql = 'INSERT INTO users(username, password, firstname, lastname, email) VALUES("admin", "password", "Admin", "User", "admin@invalid.com")'

	conn = self.connect()
	c = conn.cursor()

	c.execute(user_table_sql)

        User().create("admin", "password", "Admin", "User", "example@invalid.com", "admin")

	conn.commit()
	conn.close()

    def __init__(self):
        if os.path.exists(self.dbpath) == False:
	    print "[?] Error, database wasn't found..."
	    self.setup()
	    print "[!] Done, database was created"
""" Class for handling database interactions related to Users """
class User:
    def __init__(self):
        pass

    def create(self, username=None, password=None, firstname=None, lastname=None, email=None, role=None):
        if username == None or password == None or firstname == None or lastname == None or email == None or role == None:
	    return False
	else:
	    query = 'INSERT INTO users(username, password, firstname, lastname, email, role) VALUES("{usr}", "{passw}", "{fname}", "{lname}", "{mail}", "{urole}")'.format(usr=username, passw=password, fname=firstname, lname=lastname, mail=email, urole=role)
	    conn = Database().connect()

	    c = conn.cursor()
	    c.row_factory = sqlite3.Row
	    try:
	        c.execute(query)
                c.commit()
		conn.close()
		return True
	    except:
	        conn.close()
	        return False

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
 

""" Default route """
@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return login()

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

""" Start the Flask application """
if __name__ == "__main__":
    Database()
    app.run(debug=True, host='0.0.0.0', port=5000)
