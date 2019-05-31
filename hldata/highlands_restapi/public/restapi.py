#!/usr/bin/env python2
# coding: utf8

""" Imports """
from flask import Flask, render_template, jsonify
import os, json, random, string, re, sys, urllib, ConfigParser
from bson.json_util import loads, dumps
import connexion

""" Append the file path """
sys.path.append("/app/public/restapi")

""" Init the Connexion application  """
secret = os.urandom(2)

app = connexion.App(__name__, specification_dir='./restapi')
app.secret_key = secret
app.add_api('api.yml')

""" Start the Flask application """
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)

