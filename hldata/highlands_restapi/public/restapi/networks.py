#!/usr/bin/env python2
# coding: utf8

import ConfigParser
import json
import logging
import os
from datetime import datetime
from libs import zerotier_nc as ztclient

ztclient.main()

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