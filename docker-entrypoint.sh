#!/bin/sh

python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn -c ops_tools/settings/gunicorn.conf.py ops_tools.wsgi:application