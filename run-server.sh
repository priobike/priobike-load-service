#!/bin/bash

# Based on: https://gist.github.com/mjambon/79adfc5cf6b11252e78b75df50793f24

# Run postgres in the background
./run-postgres.sh

cd backend

# Run gunicorn
poetry run python manage.py migrate
poetry run python manage.py startup

pids=()

if [ "$WORKER_MODE" = "True" ]; then
    # Expose the sync API in worker mode, but only on the internal network between the containers.
    SYNC_EXPOSED="True" poetry run gunicorn backend.wsgi:application --workers 4 --bind 0.0.0.0:8001 &
    pids+=($!)

    SYNC_EXPOSED="False" poetry run gunicorn backend.wsgi:application --workers 4 --bind 0.0.0.0:8000 &
    pids+=($!)
else
    # If we are in the manager mode, we don't want to expose the sync API at all. However, we run a periodic sync.
    poetry run python manage.py sync --interval 60 --host "$WORKER_HOST" --port 8001 &
    pids+=($!)

    SYNC_EXPOSED="False" poetry run gunicorn backend.wsgi:application --workers 4 --bind 0.0.0.0:8000 &
    pids+=($!)
fi

# 'set -e' tells the shell to exit if any of the foreground command fails,
# i.e. exits with a non-zero status.
set -eu

# Wait for each specific process to terminate.
# Instead of this loop, a single call to 'wait' would wait for all the jobs
# to terminate, but it would not give us their exit status.
#
for pid in "${pids[@]}"; do
  #
  # Waiting on a specific PID makes the wait command return with the exit
  # status of that process. Because of the 'set -e' setting, any exit status
  # other than zero causes the current shell to terminate with that exit
  # status as well.
  #
  wait "$pid"
done