"""
Django settings for canvas_course_info project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

#import dj_database_url
#from django.core.exceptions import ImproperlyConfigured
#from getenv import env 

import os
from .secure import SECURE_SETTINGS

# TODO: does TLT want the static files in project/canvas_course_info or in project/? 
# this is only used for static and template files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = ['*']
DEBUG = SECURE_SETTINGS.get('enable_debug', False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djrill',
    'course_info'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_auth_lti.middleware.LTIAuthMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'canvas_course_info.urls'

WSGI_APPLICATION = 'canvas_course_info.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.ModelBackend'
)

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Display the button to offer to insert text by default
OFFER_TEXT = SECURE_SETTINGS.get('offer_text', True)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'

# Used by 'collectstatic' management command
STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'http_static'))
# STATICFILES_DIRS = (
#     os.path.normpath(os.path.join(BASE_DIR, 'course_info/static/')),
# )

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(BASE_DIR, 'course_info/templates'),
)

LTI_APPS = {
    'course_info': {# <- Cannot be changed without causing issues
        'id': 'course_info_import', # Changed from "course_info"
        'name': 'Import Course Info', # Changed from "Course Info"
        'menu_title': 'Import Course Info', # Changed from 'Course Info'
        'extensions_provider': 'canvas.instructure.com',
        'description': "A button to insert course info into canvas pages.",
        'privacy_level': 'public',
        'selection_height': '400px',
        'selection_width':'400px',
        'icon_url': STATIC_URL + 'images/course-info.png'
    }
}

# Trying to copy the env(required=True) functionality
SECRET_KEY = SECURE_SETTINGS['django_secret_key']
# if SECRET_KEY:
#     pass
# else:
#     raise KeyError

#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': SECURE_SETTINGS.get('db_default_name', 'canvas_course_info'),
        'USER': SECURE_SETTINGS.get('db_default_user', 'canvas_course_info'),
        'PASSWORD': SECURE_SETTINGS.get('db_default_password'),
        'HOST': SECURE_SETTINGS.get('db_default_host', '127.0.0.1'),
        'PORT': SECURE_SETTINGS.get('db_default_port', 5432),
} }

# unused right now 
GUNICORN_WORKERS = SECURE_SETTINGS.get('gunicorn_workers', 4)
GUNICORN_TIMEOUT = SECURE_SETTINGS.get('gunicorn_timeout', 60)

# Check if we want to do it like this or with the host and port 
#REDIS_URL = SECURE_SETTINGS.get('redis_url')

LTI_REQUEST_VALIDATOR = 'course_info.validator.LTIRequestValidator'

LTI_OAUTH_CREDENTIALS = SECURE_SETTINGS.get('lti_oath_credentials')
# {
#     SECURE_SETTINGS.get('lti_oauth_course_info_consumer_key') :
#         SECURE_SETTINGS.get('lti_oauth_course_info_consumer_secret')
# }

ICOMMONS_API_TOKEN = SECURE_SETTINGS.get('icommons_api_token')

ICOMMONS_BASE_URL = SECURE_SETTINGS.get('icommons_base_url')

# TODO: Can all this email stuff be taken out? Check with DCE. 
# # this tells django who to send app error emails to
# ADMINS = ((SECURE_SETTINGS.get('django_admin_name'), SECURE_SETTINGS.get('django_admin_email'))) 
#
# # From: addr of the app error emails
# SERVER_EMAIL = SECURE_SETTINGS.get('django_server_email', 'root@localhost')
#
# # use mandrill to send app error emails
# EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
# MANDRILL_API_KEY = SECURE_SETTINGS.get('mandrill_api_key')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'null': {
            "class": 'django.utils.log.NullHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['null', ],
        },
        'py.warnings': {
            'handlers': ['null', ],
        },
        '': {
            'handlers': ['console'],
            'level': "DEBUG",
        },
    }
}
