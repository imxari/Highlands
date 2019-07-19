#!/usr/bin/env python2
# coding: utf8

import json
import logging
import os
from datetime import datetime
from libs import zerotier_nc as ztclient

ztclient.main()

# Create a handler for /api/test
def get_status():
    data = ztclient.request("/status")
    return data