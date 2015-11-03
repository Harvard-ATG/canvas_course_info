from .base import *
from logging.config import dictConfig

ALLOWED_HOSTS = ['.tlt.harvard.edu']

# SSL is terminated at the ELB so look for this header to know that we should be in ssl mode
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True

dictConfig(LOGGING)
