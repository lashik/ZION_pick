#!/bin/sh

# This is the directory where RunPod's permanent volume will be mounted.
# We are choosing a clear, explicit name.
PERSISTENT_DIR="/persistent_storage"

# This is the directory inside the image where our code is "baked in".
APP_CODE_SOURCE="/app_code"

# Check if a key file (like server.py) is missing from the persistent volume.
# This check will only pass on the very first time the pod starts.
if [ ! -f "${PERSISTENT_DIR}/server.py" ]; then
    echo "First time setup: Copying application code to persistent volume..."
    # Copy the entire contents of our baked-in code to the volume.
    cp -r ${APP_CODE_SOURCE}/* ${PERSISTENT_DIR}/
else
    echo "Application code already exists in persistent volume. Skipping copy."
fi

# This is the crucial final step. It tells the script to now run
# whatever command was specified in the Dockerfile's CMD.
# In our case, it will run supervisord.
exec "$@"