#!/usr/bin/env python2
# coding: utf8

import json
import logging
import os
import re
from datetime import datetime
from libs import zerotier_nc as ztclient

ztclient.main()

# Create a handler for /api/network-create
def create_network(name=None):
    if name == None:
        return '{}'
    elif name == '':
        return '{}'
    elif re.match("[^A-Za-z0-9]", name):
        return '{}'
    else:
        headers_data = {
            "name": name,
            "private": True
        }

        header = json.dumps(header_data)

        data = ztclient.request("/controller/network/______", payload=headers)

# Create a handler for /api/network/{nwid}
def get_network_members(nwid=None):
    if nwid == None:
        return '{}'
    elif nwid == '':
        return '{}'
    else:
        data = ztclient.request("/controller/network/" + nwid + "/member")
        return data

# Create a handler for /api/network/{nwid}
def get_network_info(nwid=None):
    if nwid == None:
        return '{}'
    elif nwid == '':
        return '{}'
    else:
        data = ztclient.request("/controller/network/" + nwid)
        return data

# Create a handler for /api/networks
def get_networks():
    data = ztclient.request("/controller/network")
    return data