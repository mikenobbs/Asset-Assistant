#!/bin/bash
set -e

# Create only essential directories
mkdir -p /config/process /config/failed /config/backup /config/logs

# Copy default config if it doesn't exist in the mounted volume
if [ ! -f /config/config.yml ]; then
    echo "No config.yml found in /config, copying default configuration..."
    cp /app/config.yml.default /config/config.yml
fi

# Execute the main application
exec "$@"
