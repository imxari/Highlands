#!/usr/bin/env python2
# coding: utf8

""" Imports """
from flask import Flask, render_template, url_for, redirect, flash, request, session, abort
import os, json, random, string, re, sys, urllib, ConfigParser, requests
from bson.json_util import loads, dumps
from flask_htpasswd import HtPasswdAuth
from markupsafe import Markup

""" End Imports """

""" Init """
secret = os.urandom(2)

app = Flask(__name__)
app.secret_key = secret
app.config['FLASK_SECRET'] = secret
app.config['FLASK_HTPASSWD_PATH'] = '/app/.htpasswd'
app.config['FLASK_AUTH_ALL'] = True

htpasswd = HtPasswdAuth(app)

""" End Init """

""" Networks """
def ctrl_network_info(nwid=None):
    if nwid == None:
        return None
    elif nwid == '':
        return None
    else:
        response = requests.get("http://highlands_restapi/api/network/" + nwid)
        return response.json()

def ctrl_networks():
    response = requests.get("http://highlands_restapi/api/networks")
    return response.json()

@app.route('/networks')
def networks():
    resp = ctrl_networks()

    networks_data = list()
    for network in resp:
        if network == '{}':
            continue
        elif network == None:
            continue
        else:
            resp2 = ctrl_network_info(network)
            if resp2 == None:
                continue
            elif resp2 == '{}':
                continue
            else:
                networks_data.append(resp2)


    return render_template("networks.html", networks=networks_data)

""" End Networks """

""" Dashboard """
def ctrl_status():
    response = requests.get("http://highlands_restapi/api/status")
    return response.json()

@app.route('/dashboard')
@app.route('/')
def dashboard():
    resp = ctrl_status()
    return render_template("dashboard.html", status=resp)

""" End Dashboard """

# =============================================================================

""" Start """
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
""" End Start """

