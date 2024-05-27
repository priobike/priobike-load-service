curl "http://$MANAGER_HOSTNAME:$MANAGER_PORT/load.json" > /app/data/load.json
# If it fails, this means that the manager is not ready yet. 
# We don't need to try again because the manager is going to 
# push the first version of the load file to the workers.
if [ $? -ne 0 ]; then
    echo "Failed to fetch load.json from manager. This is expected if the manager is not ready yet."
    # Crash the worker so that the manager can restart it.
    exit 1
else
    echo "Fetched load.json from manager."
fi