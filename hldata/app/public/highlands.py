#!/usr/bin/env python2
# coding: utf8

""" Imports """
from flask import Flask, render_template, url_for, redirect, flash, request, session, abort
import os, json, random, string, re, ConfigParser, sys
from bson.json_util import loads, dumps
from zerotier import client as ztclient
from pymongo import MongoClient

""" Init the Flask application  """
app = Flask(__name__)
app.secret_key = os.urandom(2)

""" Get the Zerotier-One authkey """
def get_authkey():
    path = "/var/lib/zerotier-one/authtoken.secret"

    f = open(path, 'r')
    apikey = f.read()

    f.close()
    return apikey

""" Handle DELETE Zerotier-One API requests """
def zerotier_delete(uri=None, data=None, params=None):

    authkey = get_authkey()

    client = ztclient.Client('http://127.0.0.1:9993')

    headers = {"X-ZT1-Auth": authkey}
    resp = client.delete(uri, data, headers, params, 'json')
    return resp.text

""" Handle POST Zerotier-One API requests """
def zerotier_post(uri=None, data=None, params=None):

    authkey = get_authkey()

    client = ztclient.Client('http://127.0.0.1:9993')

    headers = {"X-ZT1-Auth": authkey}
    resp = client.post(uri, data, headers, params, 'json')
    return resp.text

""" Handle GET Zerotier-One API requests """
def zerotier_get(uri=None, data=None, params=None):

    authkey = get_authkey()

    client = ztclient.Client('http://127.0.0.1:9993')

    headers = {"X-ZT1-Auth": authkey}
    resp = client.get(uri, data, headers, params, 'json')
    return resp.text


# =============================================================================

""" Class for creating and ensuring that the MongoDB is configured """
class Init:
    def __init__(self):
        client = Database().init()

        dbnames = client.list_database_names()
        if 'highlands' not in dbnames:
            doc = {'username': 'admin',
                   'password': 'password',
                   'role': 'admin'}
            db = client.highlands
            db.users.insert_one(doc)



""" Class for handling MongoDB interactions """
class Database:
    def connect(self, host=None, port=None, username=None, password=None):
        if host == None:
            return None
        elif port == None:
            return None
        elif username == None:
            return None
        elif password == None:
            return None
        else:
            uri = 'mongodb://' + username + ':' + password + '@' + host + ':' + port + '/'
            try:
                client = MongoClient(uri)
                return client
            except Exception as e:
                print str(e)
                return None


    def init(self):
        Config = ConfigParser.ConfigParser()
        Config.read("/app/public/config.ini")

        username=Config.get('mongodb','user')
        password=Config.get('mongodb','pass')
        host=Config.get('mongodb','host')
        port=Config.get('mongodb','port')

        client = self.connect(host, port, username, password)
        return client

""" Class for handling Zerotier-One network interactions """
class Network:
    """ Handles the removal of a network """
    def delete(self, nwid=None):
        if nwid == None:
            return False
        else:
            try:
                zerotier_delete(uri='http://127.0.0.1:9993/controller/network/' + nwid)
                return True
            except Exception as e:
                print str(e)
                return False
            return False
    """ Handles creation of a network """
    def create(self, name=None):
        if name == None:
            return False
        else:
            try:
                if re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,\/ ]", name) != None:
                    return False
                else:
                    status = zerotier_get('http://127.0.0.1:9993/status')
                    status_dict = json.loads(status)

                    memberid = status_dict["address"]

                    data = {"name": name,
                            "private": True,
                            "v4AssignMode": {"zt": True }}
                    jsonarray = json.dumps(data)
                    uri = 'http://127.0.0.1:9993/controller/network/' + str(memberid) + "______"

                    resp = zerotier_post(uri=uri, data=jsonarray)
                    return True
            except Exception as e:
                print str(e)
                return False
            return False

""" Class for handling MongoDB related user queries"""
class User:
    def change_password(self, username=None, currentpassword=None, newpassword=None):
        if username == None:
            return False
        elif currentpassword == None:
            return False
        elif newpassword == None:
            return None
        else:
            docsearch = {"username": username,
                         "password": currentpassword}
            docreplace = {"username": username,
                          "password": newpassword}

            client = Database().init()
            database = client.highlands

            database.users.update_one(docsearch, docreplace)

            doc = database.users.find_one(docreplace)
            doc_dict = dumps(doc)

            if username in doc_dict and newpassword in doc_dict:
                return True
            else:
                return False


    def delete(self, username=None):
        if username == None:
            return False
        elif username == "admin":
            return False
        else:
            doc = {"username": username}

            client = Database().init()
            database = client.highlands

            database.users.delete_one(doc)

            doccheck = database.users.query(doc)
            doccheck_dict = dumps(doccheck)

            if username in doccheck_dict == True:
                return False
            else:
                return True

    def create(self, username=None, password=None, role=None):
        if username == None:
            return False
        elif password == None:
            return False
        elif role == None:
            return False
        else:
            checkQuery = {"username": username}
            client = Database().init()
            database = client.highlands
            
            doc = database.users.find(query)
            doc_dict = dumps(doc)

            if username in doc_dict == True:
                return False
            else:
                newdoc = {"username": username,
                          "password": password,
                          "role": role}
                database.users.insert_one(newdoc)
                return True


    def login(self, username=None, password=None):
        if username == None:
            return False
        elif password == None:
            return False
        else:
            client = Database().init()
            database = client.highlands
            query = {'username': username, 'password': password}

            doc = database.users.find(query)
            doc_dict = dumps(doc)
            if username in doc_dict and password in doc_dict:
                return True
            else:
                return False

# =============================================================================

@app.route('/networks')
def networks():
    networks_json = zerotier_get(uri='http://127.0.0.1:9993/controller/network')
    
    networks_dict = json.loads(networks_json)

    dicts = list()
    for nwid in networks_dict:
        network_info = zerotier_get(uri='http://127.0.0.1:9993/controller/network/' + nwid)
        if network_info == "{}":
            continue
        elif network_info == None:
            continue
        else:
            dicts.append(json.loads(network_info))

    print str(dicts)
    return render_template('networks.html', networks=dicts)

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
    status_json = zerotier_get(uri='http://127.0.0.1:9993/status')
    status_dict = json.loads(status_json)
    return render_template('dashboard.html', status=status_dict)

""" Network-Delete """
@app.route('/network-delete', methods=['GET'])
def networkdelete():
    if session.get('logged_in') != True:
        return login()

    GET_NETWORK_NWID = str(request.args.get('nwid'))
    result = Network().delete(nwid=GET_NETWORK_NWID)
    if result == True:
        flash("OK-DELETED")
        return networks()
    else:
        flash("ERROR-DELETED")
        return networks()

""" Network-Create check """
@app.route('/createnetworkcheck', methods=['POST'])
def networkcreatecheck():
    if session.get('logged_in') != True:
        return login()


    POST_NETWORK_NAME = str(request.form['network-name'])

    result = Network().create(name=POST_NETWORK_NAME)

    if result == True:
        flash("OK-CREATED")
        return networks()
    else:
        flash("ERROR-CREATED")
        return networks()

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
    Init()
    app.run(debug=True, host='0.0.0.0', port=5000)

