FROM bikenow.vkw.tu-dresden.de/priobike/priobike-nginx:v1.0

# Install pip
RUN apt-get update && apt-get install -y python3-pip

# Install cron and crontab
RUN apt-get install -y cron

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Set timezone to Berlin
RUN ln -snf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && echo Europe/Berlin > /etc/timezone

# Make cronjobs
RUN crontab -l | { cat; echo "* * * * * python3 /app/estimate.py /usr/share/nginx/html/load.json"; } | crontab -

# Expose port 80
EXPOSE 80

# Run cron in the background
CMD python3 /app/estimate.py /usr/share/nginx/html/load.json && cron && nginx -g "daemon off;"