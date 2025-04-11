#!/bin/sh
set -e

# wait for the database service to be available
./backend/scripts/wait_for_db.sh "${MYSQL_HOST}" "${MYSQL_PORT}" "${MYSQL_USER}" "${MYSQL_PASSWORD}"

# Run migrations
# Check if alembic/versions is empty
if [ -z "$(ls -A ./backend/alembic/versions)" ]; then
    echo "Generating Alembic migration..."
    alembic -c ./backend/alembic.ini revision --autogenerate -m "Initial migration"
fi

# Run any pre-start tasks
echo "Initialyse DB and data..."
echo "Checking if pre_start.sh exists at $(pwd)/backend/scripts/pre_start.sh"
ls -l $(pwd)/backend/scripts/pre_start.sh
if ! ./backend/scripts/pre_start.sh; then
    echo "Failed to initialise DB and data"
    exit 1  # Ensure the script exits if needed
fi

# Start the FastAPI server
if ! uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload; then
    echo "Uvicorn failed to start. Dropping to a shell for debugging."
    exit 1  # Ensure the script exits if needed
fi