#!/bin/sh
set -e

# Usage: ./wait-for-db.sh <db_host> <db_port> <db_user> <db_password>
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <db_host> <db_port> <db_user> <db_password>"
    exit 1
fi

DB_HOST="$1"
DB_PORT="$2"
DB_USER="$3"
DB_PASSWORD="$4"
MAX_ATTEMPTS=15
SLEEP_SECONDS=5
attempt_num=1

echo "Waiting for MySQL database at ${DB_HOST}:${DB_PORT}..."

until mysqladmin ping --host="${DB_HOST}" --port="${DB_PORT}" --user="${DB_USER}" --password="${DB_PASSWORD}" --silent; do
    if [ ${attempt_num} -ge ${MAX_ATTEMPTS} ]; then
        echo "Database ${DB_HOST}:${DB_PORT} did not become available after ${MAX_ATTEMPTS} attempts."
        exit 1
    fi
    echo "Attempt ${attempt_num}/${MAX_ATTEMPTS}: Database is not available yet. Waiting ${SLEEP_SECONDS} seconds..."
    attempt_num=$((attempt_num + 1))
    sleep ${SLEEP_SECONDS}
done

echo "Database ${DB_HOST}:${DB_PORT} is available."