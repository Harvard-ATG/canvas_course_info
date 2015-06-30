# to activate these settings, execute ./manage.py runserver --settings=dce_course_info.settings.local
from .aws import *

ENV_NAME = 'local'
INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG = SECURE_SETTINGS.get('enable_debug', True)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# Example ID for local dev: won't be getting a real course instance id from LTI launch params.
# TODO: this doesn't have to be hidden, right?
# It will make fresh installs down the line much easier to start with.
COURSE_INSTANCE_ID = "312976"