# to activate these settings, execute ./manage.py runserver --settings=canvas_course_info.settings.local

from .base import *
from logging.config import dictConfig

dictConfig(LOGGING)

ENV_NAME = 'local'
INSTALLED_APPS += ('debug_toolbar', 'sslserver',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG = SECURE_SETTINGS.get('enable_debug', True)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# Example ID for local dev: won't be getting a real course instance id from LTI launch params.
COURSE_INSTANCE_ID = SECURE_SETTINGS.get('course_instance_id')
if COURSE_INSTANCE_ID:
    COURSE_INSTANCE_ID = str(COURSE_INSTANCE_ID)

CANVAS_URL = SECURE_SETTINGS.get('canvas_url', 'https://canvas.harvard.edu')

SELENIUM_CONFIG = {
    'canvas_base_url': CANVAS_URL,
    'edit_page_url_path': '/courses/7162/pages/course-information/edit',
    'run_locally': False,
    'selenium_grid_url': SECURE_SETTINGS.get('selenium_grid_url'),
    'selenium_password': SECURE_SETTINGS.get('selenium_password'),
    'selenium_username': SECURE_SETTINGS.get('selenium_user'),
    'use_htmlrunner': SECURE_SETTINGS.get('selenium_use_htmlrunner', True),
    'widget_url': 'https://canvas-course-info.dev.tlt.harvard.edu/course_info/widget.html',
}
