#!/bin/bash

# Change directory to /app
cd /app

# Start the Zerotier-One service
/var/lib/zerotier-one/zerotier-one &

# Start the Flask Application
python /app/public/restapi.py
