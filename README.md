# Highlands

## Warning
Highlands is currently in BETA stages of development and may not be fully functional. When using this project at this current point in time expect issues.

## Prerequisites
------
Before using Highlands ensure the system running Highlands meets the following requirements:  
1. Minimum Docker version: 18.09.4 or higher  
2. Docker-Compose version 1.18.0 or higher  
3. Docker-Py version 2.6.1 or higher  
4. CPython version: 2.7.13 or higher  
5. OpenSSL version: 1.0.1t or higher  
6. Git version 1.8.3.1 or higher
7. apache-utils(Debian based) or httpd-tools(RHEL based)
  
## Install
------
To install Highlands please follow the steps below:  
1. Clone the repository:  
``` cd /tmp && git clone https://github.com/h0lysp4nk/Highlands.git && mv /tmp/Highlands /opt/highlands ```
2. After cloning the repository we need to generate a .htpasswd file by running the following command:  
``` htpasswd -c /opt/highlands/hldata/app/.htpasswd <your_username> ```  
If you want to add another user in the future use the command below and copy the stdout to the .htpasswd file:  
``` htpasswd -n <your_username> ```
3. Now we've setup the authentication enter the directory of the repository and run the bash script:   
``` bash highlands.sh install ```
4. Once the script has finished Highlands is successfully installed, you can view the usage of the above script by typing the following command:  
``` bash highlands.sh ```

## Web Interface
------
The default web interface port for Highlands is '15600', you can reach it by going to: http://x.x.x.x:15600. Highlands is designed to be put behind a reverse proxy that serves the site over HTTPS. You can customize the port that the web interface is served on by modifying the port in the '.env' file.

## Bug reporting
------
If you're experiencing any issues with Highlands please open an issue under this repository detailing the issue. Please ensure that you provide details about your environment such as operating system, kernal and docker versions etc. If your issue is missing details it will either be put on hold or be closed.

## Credits
------
**lflare** - Created the Zerotier API used in this project: https://github.com/lflare/zerotier-nc

