"""
Django settings for canvas_course_info project.

For more information on this file, see
https://docs.djangoproject.com/en/<Django Version>/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/<Django Version>/ref/settings/
"""

import logging
import os
from dj_secure_settings.loader import load_secure_settings
from icommons_common.logging import JSON_LOG_FORMAT, ContextFilter

SECURE_SETTINGS = load_secure_settings()
# TODO: does TLT want the static files in project/canvas_course_info or in project/?
# this is only used for static and template files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = ['*']
ALLOWED_CIDR_NETS = [SECURE_SETTINGS.get('vpc_cidr_block')]
DEBUG = SECURE_SETTINGS.get('enable_debug', False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'course_info',
    'icommons_ui',
    'watchman',
]

MIDDLEWARE = [
    'allow_cidr.middleware.AllowCIDRMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_auth_lti.middleware.LTIAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'

# Used by 'collectstatic' management command
STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'http_static'))
# STATICFILES_DIRS = (
#     os.path.normpath(os.path.join(BASE_DIR, 'course_info/static/')),
# )

# see https://docs.djangoproject.com/en/1.10/ref/templates/upgrading/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'course_info/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LTI_APPS = {
    'course_info': {
        'id': 'course_info_import',
        'name': 'Import Course Info',
        'menu_title': 'Course Info',
        'extensions_provider': 'canvas.instructure.com',
        'description': "A button to insert course info into canvas pages.",
        'privacy_level': 'public',
        'selection_height': '400px',
        'selection_width': '400px',
        'icon_url': 'images/course-info.png'
    }
}

SECRET_KEY = SECURE_SETTINGS.get('django_secret_key', 'changeme')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': SECURE_SETTINGS.get('db_default_name', 'canvas_course_info'),
        'USER': SECURE_SETTINGS.get('db_default_user', 'canvas_course_info'),
        'PASSWORD': SECURE_SETTINGS.get('db_default_password'),
        'HOST': SECURE_SETTINGS.get('db_default_host', '127.0.0.1'),
        'PORT': SECURE_SETTINGS.get('db_default_port', 5432),
} }

# unused right now
# GUNICORN_WORKERS = SECURE_SETTINGS.get('gunicorn_workers', 4)
# GUNICORN_TIMEOUT = SECURE_SETTINGS.get('gunicorn_timeout', 60)

# Cache
# https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES

REDIS_HOST = SECURE_SETTINGS.get('redis_host', '127.0.0.1')
REDIS_PORT = SECURE_SETTINGS.get('redis_port', '6379')
# used by LTIRequestValidator
REDIS_URL = "redis://{}:{}/0".format(REDIS_HOST, REDIS_PORT)

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
        'KEY_PREFIX': 'canvas_course_info',  # Provide a unique value for intra-app cache
        # See following for default timeout (5 minutes as of 1.7):
        # https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES-TIMEOUT
        'TIMEOUT': SECURE_SETTINGS.get('default_cache_timeout_secs', 300),
    }
}

LTI_REQUEST_VALIDATOR = 'course_info.validator.LTIRequestValidator'
LTI_OAUTH_CREDENTIALS = SECURE_SETTINGS.get('lti_oauth_credentials')

ICOMMONS_API_TOKEN = SECURE_SETTINGS.get('icommons_api_token')
ICOMMONS_BASE_URL = SECURE_SETTINGS.get('icommons_base_url')
ICOMMONS_API_PATH = '/api/course/v2/'
ICOMMONS_REST_API_SKIP_CERT_VERIFICATION = False


# Logging

class ContextFilter(logging.Filter):
    def __init__(self, **kwargs):
        self.extra = kwargs

    def filter(self, record):

        for k in self.extra:
            setattr(record, k, self.extra[k])

        return True

# Turn off default Django logging
# https://docs.djangoproject.com/en/1.8/topics/logging/#disabling-logging-configuration
#LOGGING_CONFIG = None


_DEFAULT_LOG_LEVEL = SECURE_SETTINGS.get('log_level', logging.DEBUG)
_LOG_ROOT = SECURE_SETTINGS.get('log_root', '')
_JSON_LOG_FORMAT = '%(asctime)s %(created)f %(exc_info)s %(filename)s %(funcName)s %(levelname)s %(levelno)s %(name)s %(lineno)d %(module)s %(message)s %(pathname)s %(process)s'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s\t%(asctime)s.%(msecs)03dZ\t%(name)s:%(lineno)s\t%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': _JSON_LOG_FORMAT,
        },
        'simple': {
            'format': '%(levelname)s\t%(name)s:%(lineno)s\t%(message)s',
        },
    },
    'filters': {
        'context': {
            '()': 'canvas_course_info.settings.base.ContextFilter',
            'env': SECURE_SETTINGS.get('env_name'),
            'project': 'canvas_course_info',
            'department': 'uw',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'default': {
            'class': 'splunk_handler.SplunkHandler',
            'formatter': 'json',
            'sourcetype': '_json',
            'source': 'django-canvas_course_info',
            'host': 'http-inputs-harvard.splunkcloud.com',
            'port': '443',
            'index': 'soc-isites',
            'token': SECURE_SETTINGS['splunk_token'],
            'level': _DEFAULT_LOG_LEVEL,
            'filters': ['context'],
        },
        'gunicorn': {
            'class': 'splunk_handler.SplunkHandler',
            'formatter': 'json',
            'sourcetype': '_json',
            'source': 'gunicorn-canvas_course_info',
            'host': 'http-inputs-harvard.splunkcloud.com',
            'port': '443',
            'index': 'soc-isites',
            'token': SECURE_SETTINGS['splunk_token'],
            'level': _DEFAULT_LOG_LEVEL,
            'filters': ['context'],
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
    },
    # This is the default logger for any apps or libraries that use the logger
    # package, but are not represented in the `loggers` dict below.  A level
    # must be set and handlers defined.  Setting this logger is equivalent to
    # setting and empty string logger in the loggers dict below, but the separation
    # here is a bit more explicit.  See link for more details:
    # https://docs.python.org/2.7/library/logging.config.html#dictionary-schema-details
    'root': {
        'level': logging.INFO,
        'handlers': ['default', 'console'],
    },
    'loggers': {
        'gunicorn': {
            'handlers': ['gunicorn', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'default'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
            'propagate': False,
        },
        'course_info': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        }
    },
}

WATCHMAN_TOKENS = SECURE_SETTINGS['watchman_token']
WATCHMAN_TOKEN_NAME = SECURE_SETTINGS['watchman_token_name']
WATCHMAN_CHECKS = (
    'watchman.checks.databases',
    'watchman.checks.caches',
)
