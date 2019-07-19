#!/bin/bash

# =============================================================================
#
# Highlands
# https://github.com/h0lysp4nk/Highlands
#
# =============================================================================

echo '    __  ___       __    __                __     '
echo '   / / / (_)___ _/ /_  / /___ _____  ____/ /____ '
echo '  / /_/ / / __ `/ __ \/ / __ `/ __ \/ __  / ___/ '
echo ' / __  / / /_/ / / / / / /_/ / / / / /_/ (__  )  '
echo '/_/ /_/_/\__, /_/ /_/_/\__,_/_/ /_/\__,_/____/   '
echo '        /____/                                   '
echo
echo '==================================================='
echo
echo

# Set dir
script_dir=`dirname $0`
cd $script_dir/hldata

# Handle cli input
case $1 in
	"ps")
		# Get the status of highlands
		docker-compose ps

		# Check to see if that command executed successfully
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

		# Check to see if that command executed successfully
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

		# Check to see if that command executed successfully
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
		docker-compose up -d

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
	"uninstall")
		# Uninstall Highlands
		docker-compose down

		# Check to see if that command executed successfully
		if [ $? -eq 0 ]; then
			echo "[!] Highlands containers were successfully destroyed!"
			echo "[!] To finish the removal of Highlands type: 'docker system prune' ALTHOUGH be careful as this will remove any dangling containers/images! Ensure that before running this command that all you're docker containres are online!"
		else
			echo "[!] Highlands containers couldn't be destroyed!"
			exit 1
		fi;;
	"install")
		# Install Highlands
        docker network create highlands

		# Check to see if that command executed successfully
		if [ $? -eq 0 ]; then
			# Success
			echo "[!] Highlands docker network created!"
		else
			# Failure
			echo "[!] Highlands docker network couldn't be created! Does it already exist?"
		fi

		docker-compose up -d --build

		# Check to see if that command executed successfully
		if [ $? -eq 0 ]; then
			# Success
			echo "[!] Highlands was successfully started!"
		else
			# Failure
			echo "[!] Highlands couldn't be installed!"
			exit 1
		fi;;
	*)
		echo "[!] Usage: ./highlands.sh <start|stop|restart|ps|install>";;
esac

