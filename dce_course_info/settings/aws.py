"""
Django settings for dce_course_info project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from getenv import env
from .secure import SECURE_SETTINGS

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

ROOT_URLCONF = 'dce_course_info.urls'

WSGI_APPLICATION = 'dce_course_info.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.ModelBackend'
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
# Used by 'collectstatic' management command
STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'http_static/'))
# print("STATIC_ROOT: " +  str(STATIC_ROOT))
STATICFILES_DIRS = (
    os.path.normpath(os.path.join(BASE_DIR, 'course_info/static/')),
)

#TODO: move this out of prod
# if you want to test locally and aren't getting real course instance ids from LTI launch params.
# COURSE_INSTANCE_ID=env('COURSE_INSTANCE_ID')
try:
    COURSE_INSTANCE_ID = str(SECURE_SETTINGS.get('COURSE_INSTANCE_ID'))
except:
    #log something?
    pass

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

# SECRET_KEY = env('DJANGO_SECRET_KEY', required=True)
# Trying to copy the env(required=True) functionality
SECRET_KEY = SECURE_SETTINGS.get('DJANGO_SECRET_KEY')
if SECRET_KEY:
    pass
else:
    raise KeyError

# this tells django who to send app error emails to
# ADMINS = ((env('DJANGO_ADMIN_NAME'), env('DJANGO_ADMIN_EMAIL')),)
ADMINS = ((SECURE_SETTINGS.get('DJANGO_ADMIN_NAME'), SECURE_SETTINGS.get('DJANGO_ADMIN_EMAIL')))


# From: addr of the app error emails
# SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', 'root@localhost')
SERVER_EMAIL = SECURE_SETTINGS.get('DJANGO_SERVER_EMAIL', 'root@localhost')


# use mandrill to send app error emails
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
# MANDRILL_API_KEY = env('MANDRILL_APIKEY')
MANDRILL_API_KEY = SECURE_SETTINGS.get('MANDRILL_APIKEY')

# depends on DATABASE_URL being set in your env. See https://github.com/kennethreitz/dj-database-url
# you can also set DJANGO_DATABASE_DEFAULT_ENGINE if you want to override the
# default engine, e.g., using https://github.com/kennethreitz/django-postgrespool/
# default engine, e.g., using https://github.com/kennethreitz/django-postgrespool/
# DATABASES = {
#     'default': dj_database_url.config(
#         # engine=env('DJANGO_DATABASE_DEFAULT_ENGINE', None))
#         engine = SECURE_SETTINGS.get('DJANGO_DATABASE_DEFAULT_ENGINE', None)
#     )
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': SECURE_SETTINGS.get('db_default_name', 'dcei_db'),
        'USER': SECURE_SETTINGS.get('db_default_user', 'dce_course_info'),
        'PASSWORD': SECURE_SETTINGS.get('db_default_password'),
        'HOST': SECURE_SETTINGS.get('db_default_host', '127.0.0.1'),
        'PORT': SECURE_SETTINGS.get('db_default_port', 5432),
} }

# REDIS_URL = env('REDIS_URL')
# Check if we want to do it like this or with the host and port
REDIS_URL = SECURE_SETTINGS.get('REDIS_URL')

LTI_REQUEST_VALIDATOR = 'course_info.validator.LTIRequestValidator'

LTI_OAUTH_CREDENTIALS = {
    SECURE_SETTINGS.get('LTI_OAUTH_COURSE_INFO_CONSUMER_KEY') :
        SECURE_SETTINGS.get('LTI_OAUTH_COURSE_INFO_CONSUMER_SECRET')

    # env('LTI_OAUTH_COURSE_INFO_CONSUMER_KEY'): env(
    #     'LTI_OAUTH_COURSE_INFO_CONSUMER_SECRET')
}

# Display the button to offer to insert text by default
OFFER_TEXT = SECURE_SETTINGS.get('OFFER_TEXT', True)

# ICOMMONS_API_TOKEN = env('ICOMMONS_API_TOKEN')
ICOMMONS_API_TOKEN = SECURE_SETTINGS.get('ICOMMONS_API_TOKEN')

# ICOMMONS_BASE_URL = env('ICOMMONS_BASE_URL')
ICOMMONS_BASE_URL = SECURE_SETTINGS.get('ICOMMONS_BASE_URL')

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