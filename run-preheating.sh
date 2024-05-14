#!/bin/bash

echo "Preheating the docker image..."

# Run postgres in the background
./run-postgres.sh

# Check if previous command failed. If it did, exit
ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to start postgres"
    exit $ret
fi

# Run the migration script
poetry run python backend/manage.py migrate

echo "Preheating complete!"