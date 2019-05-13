#!/usr/bin/env python2
# coding: utf8

""" Imports """
from flask import Flask, render_template, url_for, redirect, flash, request, session, abort
import os, json, random, string, re, sys
from bson.json_util import loads, dumps
from zerotier import client as ztclient
from flask_htpasswd import HtPasswdAuth

""" Init the Flask application  """
secret = os.urandom(2)

app = Flask(__name__)
app.secret_key = secret
app.config['FLASK_SECRET'] = secret
app.config['FLASK_HTPASSWD_PATH'] = '/app/.htpasswd'
app.config['FLASK_AUTH_ALL'] = True

htpasswd = HtPasswdAuth(app)

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
        elif len(name) >= 33:
            return False
        else:
            try:
                if re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,.\/ ]", name) != None:
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

""" Dashboard """
@app.route('/')
@app.route('/dashboard')
def dashboard():
    status_json = zerotier_get(uri='http://127.0.0.1:9993/status')
    status_dict = json.loads(status_json)
    return render_template('dashboard.html', status=status_dict)

""" Network-Delete """
@app.route('/network-delete', methods=['GET'])
@htpasswd.required
def networkdelete():
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
    POST_NETWORK_NAME = str(request.form['network-name'])

    result = Network().create(name=POST_NETWORK_NAME)

    if result == True:
        flash("OK-CREATED")
        return networks()
    else:
        flash("ERROR-CREATED")
        return networks()

# =============================================================================

""" Start the Flask application """
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

