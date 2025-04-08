#!/usr/bin/env bash

set -e
set -x
# export PYTHONPATH="$(pwd)/..:$PYTHONPATH"
# Let the DB start conda run -n emon-tools-dev-fast
echo "Initialysing DB..."
python -m backend.fastapi_pre_start

# Run migrations
echo "Run Migrations"
alembic -c backend/alembic.ini upgrade head

# Create initial data in DB
echo "Create initial data in DB"
python -m backend.initial_data