#! /usr/bin/env bash

set -e
set -x
# export PYTHONPATH="$(pwd)/..:$PYTHONPATH"
# Let the DB start conda run -n emon-tools-dev-fast 
python -m emon_tools.fastapi.backend_pre_start

# Run migrations
alembic -c emon_tools/fastapi/alembic.ini upgrade head

# Create initial data in DB conda run -n emon-tools-dev-fast 
python -m emon_tools.fastapi.initial_data