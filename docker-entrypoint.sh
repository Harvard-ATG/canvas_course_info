#!/bin/sh

python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn -c canvas_course_info/settings/gunicorn.conf.py canvas_course_info.wsgi:application