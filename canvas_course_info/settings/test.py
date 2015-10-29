# ./manage.py test
from .aws import *

ENV_NAME = 'test'
DEBUG = SECURE_SETTINGS.get('enable_debug', True)

# if you want to test locally and aren't getting real course instance ids from LTI launch params.
# COURSE_INSTANCE_ID=env('COURSE_INSTANCE_ID')
COURSE_INSTANCE_ID = SECURE_SETTINGS.get('COURSE_INSTANCE_ID')
if COURSE_INSTANCE_ID :
    COURSE_INSTANCE_ID = str(COURSE_INSTANCE_ID)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'canvas_course_info',
    },
}
