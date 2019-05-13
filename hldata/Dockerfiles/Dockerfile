# Specify docker image
FROM alpine:edge

# Specify maintainer
MAINTAINER Holy, https://github.com/h0lysp4nk

# Specify user
USER root

# Add repos
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

# Add basics first
RUN apk update && apk upgrade && apk add \
	bash python2 py2-pip zerotier-one

# Setup Flask and other required pip packages
RUN pip install Flask Jinja2 Babel Flask-Babel Flask-Login Flask-Mail Flask-OpenID Flask-WTF Tempita WTForms Werkzeug blinker decorator distribute flup python-openid pytz speaklater requests enum python-dateutil bson flask-htpasswd pymongo
 
# Remove APK cache
RUN rm -rf /var/cache/apk/*

# Create web folder and start script dir
RUN mkdir -p /app && mkdir -p /app/public
RUN mkdir -p /bootstrap

# Copy start.sh to /bootstrap
COPY ./start.sh /bootstrap/start.sh

# Set permissions
RUN chmod -R 755 /bootstrap && chmod -R 755 /app

# Run the application
EXPOSE 5000
ENTRYPOINT ["/bootstrap/start.sh"]

