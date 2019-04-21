#!/bin/bash

# =============================================================================
#
# Highlands
# https://github.com/h0lysp4nk/Highlands
#
# =============================================================================

# Show Highlands banner
cat .banner.txt && echo

# Change directory into hldata
script_dir=`dirname $0`
cd $script_dir/hldata

# Handle cli input
case $1 in
	"status")
		# Get the status of highlands
		docker-compose ps
		if [ $? -eq 0 ]; then
			# Success
			echo "[!] Successfully received the status of highlands!"
			exit 0
		else
			# Failure
			echo "[!] Couldn't get the status of highlands!"
			exit 1
		fi;;
	"restart")
		# Restart Highlands
		docker-compose stop && docker-compose up -d
		if [ $? -eq 0 ]; then
			# Success
			echo "[!] Highlands restarted successfully!"
			exit 0
		else
			# Failure
			echo "[!] Highlands failed to restart!"
			exit 1
		fi;;
	"stop")
		# Stop Highlands
		docker-compose stop
		if [ $? -eq 0 ]; then
			# Success
			echo "[!] Highlands stopped successfully!"
			exit 0
		else
			# Failure
			echo "[!] Highlands failed to stop!"
			exit 1
		fi;;
	"start")
		# Start Highlands
		docker-compose -d

		# Check to see if that command executed successfully
		if [ $? -eq 0 ]; then
			# Success
			echo "[!] Highlands started successfully!"
			exit 0
		else
			# Failure
			echo "[!] Highlands failed to start!"
			exit 1
		fi;;
	"install")
		# Install Highlands
		docker-compose up -d --build
		if [ $? -eq 0 ]; then
			# Success
			echo "[!] Highlands was successfully installed and started!"
			exit 0
		else
			# Failure
			echo "[!] Highlands couldn't be installed!"
			exit 1
		fi;;
	*)
		echo "[!] Usage: ./highlands.sh <start|stop|restart>";;
esac

