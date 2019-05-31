#!/usr/bin/env python2
# coding: utf8

import ConfigParser
import json
import logging
import os
from datetime import datetime

# Create a handler for /api/test
def read():
    data = {"test": "Hello, World"}
    return data