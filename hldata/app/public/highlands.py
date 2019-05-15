#!/usr/bin/env python2
# coding: utf8

""" Imports """
from flask import Flask, render_template, url_for, redirect, flash, request, session, abort
import os, json, random, string, re, sys, urllib, ConfigParser
from bson.json_util import loads, dumps
from zerotier import client as ztclient
from flask_htpasswd import HtPasswdAuth
from markupsafe import Markup


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

@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)

@app.template_filter('member_desc')
def memberdesc_filter(s):
    desc = Member().get(s)
    return desc

@app.template_filter('member_detail')
def memberdetail_filter(n, s):
    member_detail = zerotier_get(uri='http://127.0.0.1:9993/controller/network/' + n + '/member/' + s)
    member_detail_json = loads(member_detail)
    return member_detail_json
    
@app.template_filter('members_list')
def memberlist_filter(n):
    member_list = zerotier_get(uri='http://127.0.0.1:9993/controller/network/' + n + '/member')
    member_list_json = json.loads(member_list)

    return member_list_json

# =============================================================================

""" Class for handling member desc interactions """
class Member:
    def bridge(self, nwid=None, address=None, bridged=None):
        if nwid == None or nwid == "":
            return False
        if address == None or address == "":
            return False
        elif bridged == None:
            return False
        else:
            try:
                data = {"activeBridge": bridged}

                zerotier_post(uri='http://127.0.0.1:9993/controller/network/' + nwid + '/member/' + address, data=data)

                return True
            except Exception as e:
                print str(e)
                return False
            return False

    def auth(self, nwid=None, address=None, authed=None):
        if nwid == None or nwid == "":
            return False
        if address == None or address == "":
            return False
        elif authed == None:
            return False
        else:
            try:
                data = {"authorized": authed}

                zerotier_post(uri='http://127.0.0.1:9993/controller/network/' + nwid + '/member/' + address, data=data)

                return True
            except Exception as e:
                print str(e)
                return False
            return False
    def get(self, address=None):
        if address == None or address == "":
            return None
        elif os.path.exists("/app/members.ini") == False:
            return None
        else:
            config = ConfigParser.ConfigParser()
            config.read('/app/members.ini')
            
            desc = config.get("DESCRIPTIONS", address)
            return Markup(desc)

    def add(self, address=None, description=None):
        if address == None or address == "":
            return None
        elif description == None or description == "":
            return None
        else:
            try:
                config = ConfigParser.ConfigParser()
                config.read('/app/members.ini')

                if config.has_section("DESCRIPTIONS") == False:
                    config.add_section("DESCRIPTIONS")

                config.set("DESCRIPTIONS", address, description)

                with open('/app/members.ini', 'w') as f:
                    config.write(f)
                return True
            except Exception as e:
                print str(e)
                return False
            return False
            

""" Class for handling Zerotier-One network interactions """
class Network:
    """ Handles the setup of a network """
    def setup(self, nwid=None, cidr=None, ipstart=None, ipend=None):
        if nwid == None:
            return False
        elif cidr == None:
            return False
        elif ipstart == None:
            return False
        elif ipend == None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,.\/ ]", nwid) != None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,\ ]", cidr) != None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,\/ ]", ipstart) != None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,\/ ]", ipend) != None:
            return False
        else:
            try:
                data = {"private": True,
                        "v4AssignMode": { "zt": True },
                        "ipAssignmentPools": [{ "ipRangeStart": ipstart, "ipRangeEnd": ipend }],
                        "routes": [ { "target": cidr } ]}
                zerotier_post(uri='http://127.0.0.1:9993/controller/network/' + nwid, data=data)
                return True
            except Exception as e:
                print str(e)
                return False
            return False

    """ Handles the adding of a network route """
    def add_route(self, nwid=None, route=None, via=None):
        if nwid == None:
            return False
        elif route == None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,.\/ ]", nwid) != None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,\ ]", route) != None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,\/ ]", via) != None:
            return False
        else:
            try:
                network = zerotier_get(uri='http://127.0.0.1:9993/controller/network/' + nwid)
                network_json = loads(network)

                routes = network_json['routes']
                for element in routes:
                    if element['target'] == route:
                        return False

                new_route = {"target": route,
                             "via": via}
                routes.append(new_route)

                data = {"routes": routes}

                zerotier_post(uri='http://127.0.0.1:9993/controller/network/' + nwid, data=data)
                return True
            except Exception as e:
                print str(e)
                return False
            return False

    """ Handles the removal of a networks route """
    def delete_route(self, nwid=None, route=None):
        if nwid == None:
            return False
        elif route == None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,.\/ ]", nwid) != None:
            return False
        elif re.search("[-!$%^&*()_+|~=`{}\[\]:\";'<>?,\ ]", route) != None:
            return False
        else:
            try:
                network = zerotier_get(uri='http://127.0.0.1:9993/controller/network/' + nwid)
                network_json = loads(network)

                routes = network_json['routes']

                i = 0
                for element in routes:
                    if element['target'] == route:
                        print "YES"
                        del routes[i]
                    ++i

                print str(routes)

                data = {"routes": routes}

                zerotier_post(uri='http://127.0.0.1:9993/controller/network/' + nwid, data=data)

                return True
            except Exception as e:
                print str(e)
                return False
            return False


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
        if name == None or name == "":
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

    return render_template('networks.html', networks=dicts)

""" Dashboard """
@app.route('/')
@app.route('/dashboard')
def dashboard():
    status_json = zerotier_get(uri='http://127.0.0.1:9993/status')
    status_dict = json.loads(status_json)
    return render_template('dashboard.html', status=status_dict)

""" Add-MemberDesc """
@app.route('/setmemberdesc', methods=['POST'])
def addmemberdesc():
    POST_MEMBER_ID = str(request.form['memberid'])
    POST_MEMBER_DESC = str(request.form['description'])

    result = Member().add(address=POST_MEMBER_ID, description=POST_MEMBER_DESC)

    if result == True:
        flash("Success! Member description set!")
        return networks()
    else:
        flash("Error! Member description couldn't be set!")
        return networks()

""" Member-UnBridge """
@app.route('/member-unbridge', methods=['GET'])
def memberunbridge():
    GET_NETWORK_NWID = str(request.args.get('nwid'))
    GET_MEMBER_ADDRESS = str(request.args.get('address'))

    result = Member().bridge(nwid=GET_NETWORK_NWID, address=GET_MEMBER_ADDRESS, bridged=False)
    if result == True:
        flash("Success! Member unbridged!")
        return networks()
    else:
        flash("Error! Member couldn't be unbridged!")
        return networks()

""" Member-Bridge """
@app.route('/member-bridge', methods=['GET'])
def memberbridge():
    GET_NETWORK_NWID = str(request.args.get('nwid'))
    GET_MEMBER_ADDRESS = str(request.args.get('address'))

    result = Member().bridge(nwid=GET_NETWORK_NWID, address=GET_MEMBER_ADDRESS, bridged=True)
    if result == True:
        flash("Success! Member bridged!")
        return networks()
    else:
        flash("Error! Member couldn't be bridged!")
        return networks()

""" Member-UnAuth """
@app.route('/member-unauth', methods=['GET'])
def memberunauth():
    GET_NETWORK_NWID = str(request.args.get('nwid'))
    GET_MEMBER_ADDRESS = str(request.args.get('address'))

    result = Member().auth(nwid=GET_NETWORK_NWID, address=GET_MEMBER_ADDRESS, authed=False)
    if result == True:
        flash("Success! Member unauthorized!")
        return networks()
    else:
        flash("Error! Member couldn't be unauthorized!")
        return networks()

""" Member-Auth """
@app.route('/member-auth', methods=['GET'])
def memberauth():
    GET_NETWORK_NWID = str(request.args.get('nwid'))
    GET_MEMBER_ADDRESS = str(request.args.get('address'))

    result = Member().auth(nwid=GET_NETWORK_NWID, address=GET_MEMBER_ADDRESS, authed=True)
    if result == True:
        flash("Success! Member authorized!")
        return networks()
    else:
        flash("Error! Member couldn't be authorized!")
        return networks()

""" Route-Delete """
@app.route('/route-delete', methods=['GET'])
def routedelete():
    GET_NETWORK_NWID = str(request.args.get('nwid'))
    GET_ROUTE_TARGET = str(request.args.get('route'))
    GET_ROUTE_TARGET_DECODED = str(urllib.unquote(GET_ROUTE_TARGET))
    result = Network().delete_route(nwid=GET_NETWORK_NWID, route=GET_ROUTE_TARGET_DECODED)
    if result == True:
        flash("Success! Route was deleted!")
        return networks()
    else:
        flash("Error! Route couldn't be deleted!")
        return networks()

""" Route-Add """
@app.route('/addroutecheck', methods=['POST'])
def addroutecheck():
    POST_NETWORK_NWID = str(request.form['network-nwid'])
    POST_ROUTE_TARGET = str(request.form['target'])
    POST_ROUTE_VIA = str(request.form['via'])

    result = Network().add_route(POST_NETWORK_NWID, POST_ROUTE_TARGET, POST_ROUTE_VIA)

    if result == True:
        flash("Success! Route was added successfully")
        return networks()
    else:
        flash("Error! Route couldn't be added!")
        return networks()

""" Network-Delete """
@app.route('/network-delete', methods=['GET'])
def networkdelete():
    GET_NETWORK_NWID = str(request.args.get('nwid'))
    result = Network().delete(nwid=GET_NETWORK_NWID)
    if result == True:
        flash("Success! Network was deleted!")
        return networks()
    else:
        flash("Error! Network couldn't be deleted!")
        return networks()

""" Network-Setup check """
@app.route('/setupnetworkcheck', methods=['POST'])
def networksetupcheck():
    POST_NETWORK_NWID = str(request.form['network-nwid'])
    POST_NETWORK_CIDR = str(request.form['cidr'])
    POST_NETWORK_IPSTART = str(request.form['ipassignment-start'])
    POST_NETWORK_IPEND = str(request.form['ipassignment-end'])

    result = Network().setup(nwid=POST_NETWORK_NWID, cidr=POST_NETWORK_CIDR, ipstart=POST_NETWORK_IPSTART, ipend=POST_NETWORK_IPEND)

    if result == True:
        flash("Success! IP Assignments and default route set!")
        return networks()
    else:
        flash("Error! Couldn't set IP Assignments or default route!")
        return networks()

""" Network-Create check """
@app.route('/createnetworkcheck', methods=['POST'])
def networkcreatecheck():
    POST_NETWORK_NAME = str(request.form['network-name'])

    result = Network().create(name=POST_NETWORK_NAME)

    if result == True:
        flash("Success! Network was created!")
        return networks()
    else:
        flash("Error! Network couldn't be created!")
        return networks()

# =============================================================================

""" Start the Flask application """
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

