#!/bin/sh
set -e
set -x

# Ensure PYTHONPATH is set correctly
export PYTHONPATH=/opt/emon_tools

echo "Current working directory: $(pwd)"

echo "Initialysing DB..."
python -m backend.fastapi_pre_start || { echo "Failed to initialise DB"; exit 1; }

# Run migrations
echo "Run Migrations"
alembic -c ./backend/alembic.ini upgrade head || { echo "Migration failed"; exit 1; }

# Create initial data in DB
echo "Create initial data in DB"
python -m backend.initial_data || { echo "Failed to create initial data"; exit 1; }
