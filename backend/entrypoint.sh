#!/bin/sh
set -e

echo "Running collectstatic..."
python manage.py collectstatic --noinput --clear

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating cache table..."
python manage.py createcachetable

echo "Starting Gunicorn..."
exec "$@"