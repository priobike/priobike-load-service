#!/bin/bash

set -e

# Print env vars to file
env > /app/env.txt

# Install cronjobs
env | crontab -
crontab -l | { cat; echo "* * * * * python3 /app/estimate.py /usr/share/nginx/html/load.json /usr/share/nginx/html/metrics.txt >> /var/log/cron.log 2>&1"; } | crontab -

# Execute the script once
python3 /app/estimate.py /usr/share/nginx/html/load.json /usr/share/nginx/html/metrics.txt

# Start cron
service cron start

# Check if cron is running
if ps aux | grep '[c]ron' > /dev/null; then
  echo "Cron is running"
else
  echo "Cron failed to start"
  exit 1
fi

# Start nginx
nginx -g "daemon off;"