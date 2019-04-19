""" Imports """
from flask import Flask, render_template, url_for, redirect, flash, request, session, abort
import os
import sqlite3

""" Init the Flask application  """
app = Flask(__name__)
app.secret_key = os.urandom(2)

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

    conn = sqlite3.connect("/app/highlands.db")

    c = conn.cursor()
    c.execute("SELECT username,password FROM users WHERE username='{un}' AND password='{pw}'".format(un=POST_USERNAME, pw=POST_PASSWORD))

    rows = c.fetchall()

    usernameCorrect = False
    passwordCorrect = False
    for row in rows:
        for value in row:
	    if POST_USERNAME == value:
	        usernameCorrect = True
	    elif POST_PASSWORD == value:
	        passwordCorrect = True

    result = False
    if usernameCorrect == True and passwordCorrect == True:
        result = True

    if result:
        session['logged_in'] = True
        session['username'] = request.form['username']
        return dashboard()
    else:
        flash('Either your username or password was wrong. Try again.')
        return login()

""" Database checks/setup """
user_table_sql = 'CREATE TABLE `users`( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `username` VARCHAR(75) NOT NULL, `password` VARCHAR(75) NOT NULL, `firstname` VARCHAR(75) NOT NULL, `lastname` VARCHAR(75) NOT NULL, `email` VARCHAR(75) NOT NULL)'
default_user_sql = 'INSERT INTO users(username, password, firstname, lastname, email) VALUES("admin", "password", "Admin", "User", "admin@invalid.com")'
if os.path.exists("/app/highlands.db") == False:
    conn = sqlite3.connect("/app/highlands.db")
    c = conn.cursor()
    
    c.execute(user_table_sql)
    c.execute(default_user_sql)
    
    conn.commit()
    conn.close()

""" Start the Flask application """
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
